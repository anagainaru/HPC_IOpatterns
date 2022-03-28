# Skel-IO benchmark

Starting from the code in [https://github.com/isosc/skel-io](https://github.com/isosc/skel-io)

**Build the benchmark**

Instructions for ANDES, prerequisites include adios and cheetah3.

```
pip install cheetah3 --prefix=/autofs/nccs-svm1_home1/againaru/.local/lib/python3.6/site-packages
module load cmake
export ADIOS2_DIR=/ccs/home/againaru/adios/ADIOS2/install_andes
export PYTHONPATH=${ADIOS2_DIR}/lib64/python3.6/site-packages:/autofs/nccs-svm1_home1/againaru/.local/lib/python3.6/site-packages
export LD_LIBRARY_PATH=${ADIOS2_DIR}/lib64/:${LD_LIBRARY_PATH}
```

The Makefile in the `tests/lammps/small` folder can be used test the benchmark on a given set of applications.
```
make clean
make create
make build
make run
```

The `trace` folder needs to exist next to the Makefile containing the skel config file and the trace logs (each application needs an individual folder called `application_{i}`).
In each application folder the TAU logs need to be stord.

Example:
```
$ ls trace/*
trace/skel-io.json

trace/application1:
rank00000.trace  rank00001.trace  rank00002.trace  rank00003.trace

trace/application2:
rank00000.trace  rank00001.trace  rank00002.trace
```

**Modifications to the code**

Look for traces in application folder and not directly in the trace folder.

1. To compute the total number of rank cpp files we need to generate
```diff
diff --git a/skel_io/__skel_io.py b/skel_io/__skel_io.py
index 59156dd..807c293 100644
--- a/skel_io/__skel_io.py
+++ b/skel_io/__skel_io.py
@@ -32,7 +32,10 @@ def process (config):
     #_template_filename = f"{template_dir}/"

     # Count the trace files
-    files_in_tracedir = [t for t in os.listdir(config.tracedir) if '.trace' in t]
+    applications_in_tracedir = [t for t in os.listdir(config.tracedir) if 'application' in t]
+    files_in_tracedir = []
+    for app_path in applications_in_tracedir:
+        files_in_tracedir += [t for t in os.listdir(config.tracedir+"/"+app_path) if '.trace' in t]
     num_traces = len(files_in_tracedir)
```

2. To extract the log information from the traces

```diff
diff --git a/skel_io/__util.py b/skel_io/__util.py
index 7581c0b..02571ef 100755
--- a/skel_io/__util.py
+++ b/skel_io/__util.py
@@ -44,28 +44,37 @@ def trace_to_model(trace_dir, outfile):

   print ("Extracting traces in {} to {}".format(trace_dir, outfile) )

-
-  trace_list = glob.glob("{}/*.trace".format(trace_dir) )
-  trace_list.sort()
+  application_list = glob.glob("{}/application*".format(trace_dir) )
+  application_list.sort()
+  print ("Application list: {}".format(application_list))
+  posix_model["mapping"] = ""
+  global_rank = 0
+  application_number = 0
+  for application_dir in application_list:
-  for filename in trace_list:
-      # Get the MPI rank index
-      try:
-          rank = int(re.search('{}/rank(.+?)\.trace'.format(trace_dir), filename).group(1))
+      trace_list = glob.glob("{}/*.trace".format(application_dir) )
+      trace_list.sort()
+      print("{}: traces: {}".format(application_dir, trace_list))
+
+      for filename in trace_list:
+          # Get the MPI rank index
+          try:
+              rank = int(re.search('{}/rank(.+?)\.trace'.format(application_dir), filename).group(1))
-          print("Parsed", filename, "found", len(intrace), "events")
+              print("Parsed", filename, " (global rank ", global_rank,") found", len(intrace), "events")
+              posix_model["mapping"] += str(application_number)+","
+              global_rank += 1
+      application_number += 1

   posix_model['events'] = allevents
   posix_model['num_ranks'] = len(allevents)
   @@ -107,6 +114,7 @@ def do_posixonly(model, outfile):
             print("Parsed a rank, found ", len(posix_model['events']), " posix events")

     posix_model['num_ranks'] = doc['num_ranks']
+    posix_model["mapping"] = doc["mapping"]

     with open (outfile, 'w') as out:
         json.dump (posix_model, out, indent=3)
   @@ -148,6 +156,7 @@ def do_addcompute(model, outfile):
             print("Parsed a rank, found ", len(augmented_events), " posix events")

     posix_model['num_ranks'] = doc['num_ranks']
+    posix_model["mapping"] = doc["mapping"]

     with open (outfile, 'w') as out:
         json.dump (posix_model, out, indent=2)
```

3. Changes in the template functions to split the communicator for each application and pass the application information to each rank code.
```diff
diff --git a/tmpl/main_src_cxx.tmpl b/tmpl/main_src_cxx.tmpl
index f0f4abb..850cfa1 100644
--- a/tmpl/main_src_cxx.tmpl
+++ b/tmpl/main_src_cxx.tmpl
@@ -1,9 +1,10 @@

 \#include <iostream>
+\#include <vector>
 \#include "mpi.h"

 #for $t_rank in range($self.models['posix-model']['num_ranks'])
-void do_rank_<%='{0:05d}'.format(t_rank)%>(MPI_Comm comm);
+void do_rank_<%='{0:05d}'.format(t_rank)%>(MPI_Comm comm, int application_id);
 #end for

 std::string logfilename = "perf.json";
 @@ -14,12 +15,16 @@ int main(int argc, char** argv) {
     int rank;
     MPI_Init(&argc, &argv);
     MPI_Comm_rank (MPI_COMM_WORLD, &rank);
+    MPI_Comm new_comm;
+   std::vector<int> mapping = {$self.models['posix-model']['mapping']};
+   int color = mapping[rank];
+    MPI_Comm_split(MPI_COMM_WORLD, color, rank, &new_comm);

     if (0 == rank)
-        do_rank_00000(MPI_COMM_WORLD);
+        do_rank_00000(new_comm, color);
 #for $t_rank in range(1,$self.models['posix-model']['num_ranks'])
     else if ($t_rank == rank)
-        do_rank_<%='{0:05d}'.format(t_rank)%>(MPI_COMM_WORLD);
+        do_rank_<%='{0:05d}'.format(t_rank)%>(new_comm, color);
 #end for

     MPI_Finalize();
```

The rank code is using the application information to create output logs separate per each application.
```diff
diff --git a/tmpl/rank_src_cxx.tmpl b/tmpl/rank_src_cxx.tmpl
index 653d734..8841bce 100644
--- a/tmpl/rank_src_cxx.tmpl
+++ b/tmpl/rank_src_cxx.tmpl
@@ -633,7 +633,7 @@ for event in self.models['posix-model']['events'][int(self.arg['rank'])]:
     std::cout <<  <%='#'%>tname << ": " << tname.count() << std::endl;


-void do_rank_<%='{0:05d}'.format(int(self.arg['rank']))%> (MPI_Comm comm){
+void do_rank_<%='{0:05d}'.format(int(self.arg['rank']))%> (MPI_Comm comm, int application_id){

     int rv;
     int root = 0; // Use rank zero unless we need something else
@@ -707,7 +707,8 @@ filter = ["/proc/self/maps"]
 <%first=True%>
         // Dump json file
         std::ofstream logfile;
-        logfile.open (logfilename);
+        logfile.open ("ap"+std::to_string(application_id)+"_"+logfilename);
+
         logfile << "{\"timer_set\": [\n";
 #for $timer in $timer_list
 #if not $first
 ```
