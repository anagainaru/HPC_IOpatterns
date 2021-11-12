import sys
import pandas as pd
from collections import Counter
import seaborn as sns
from sklearn.metrics.pairwise import euclidean_distances, manhattan_distances
import matplotlib.pyplot as plt
import hdbscan
import os

sns.set()

def default_dataset(paths):
    df = pd.read_csv(paths[0])

    # Use HDBSCAN
    log_columns = set([c for c in df.columns if 'perc' in c.lower() or 'log10' in c.lower()]).difference(["POSIX_LOG10_agg_perf_by_slowest"])
    clusterer = hdbscan.HDBSCAN(min_samples=10, cluster_selection_epsilon=5, metric='manhattan', gen_min_span_tree=True, core_dist_n_jobs=8)
    clusterer.fit(df[log_columns])

    return df, clusterer

def main(top_apps=6, jobs_per_app=16):
    if len(sys.argv) < 2:
        print("Usage: %s fetures_file" %(sys.argv[0]))
        return

    df, _ = default_dataset(paths=[sys.argv[1]])
    columns = set([c for c in df.columns if 'perc' in c.lower() or 'log10' in c.lower()]).difference(["POSIX_LOG10_agg_perf_by_slowest"])

    top_applications = Counter(df.apps_short).most_common()[:top_apps]
    top_applications = [x[0] for x in top_applications] # get just the names 

    new_df = pd.DataFrame()
    for app in top_applications:
        new_df = new_df.append(df[df.apps_short == app].sample(jobs_per_app))

    mapping = {'simple': "Simple", 'warpx': "WarpX",
               'nwchem': "NWChem", 'lmp': "LAMMPS"}
    # Rename app names to preserve anonymity
    #mapping = {top_applications[0]: "Climate",        top_applications[1]: "Materials",   top_applications[2]: "Cosmology",
     #          top_applications[3]: "Fluid dynamics"}#, top_applications[4]: "Benchmark 1", top_applications[5]: "Benchmark 2"}

    new_df.apps_short = new_df.apps_short.map(mapping)
    top_applications = [mapping[x] for x in top_applications]
    
    # Calculate distances and wrap in a dataframe
    l1_distances = manhattan_distances(new_df[columns], new_df[columns])
    l2_distances = euclidean_distances(new_df[columns], new_df[columns])
    l1_distances = pd.DataFrame(l1_distances, columns=new_df.index, index=new_df.index)
    l2_distances = pd.DataFrame(l2_distances, columns=new_df.index, index=new_df.index)

    # Get colors for each row and column
    palette = sns.color_palette(n_colors=top_apps)
    lut = {app: color for app, color in zip(top_applications, palette)}
    row_colors = new_df.apps_short.map(lut)
    row_colors.name = ""

    # Draw
    cg1 = sns.clustermap(l1_distances, row_colors=row_colors, col_colors=row_colors, row_cluster=True, col_cluster=True, 
            cbar_pos=(.1, .1, .03, 0.6), xticklabels=False, yticklabels=False, robust=True, figsize=(8, 8))
    cg2 = sns.clustermap(l2_distances, row_colors=row_colors, col_colors=row_colors, row_cluster=True, col_cluster=True, 
            cbar_pos=(.1, .1, .03, 0.6), xticklabels=False, yticklabels=False, robust=True, figsize=(8, 8))

    # Hardcode labels for anonymity
    for label in top_applications:
        cg1.ax_col_dendrogram.bar(0, 0, color=lut[label], label=label)
        cg2.ax_col_dendrogram.bar(0, 0, color=lut[label], label=label)

    # Plot labels
    cg1.ax_col_dendrogram.legend(loc="center", ncol=top_apps // 3, fontsize=25)
    cg2.ax_col_dendrogram.legend(loc="center", ncol=top_apps // 3, fontsize=25)

    # Hide the dendrogram - this will also kill the legend, so we should generate two graphs and then stitch them
    # together
    cg1.ax_row_dendrogram.set_visible(False)
    cg1.ax_col_dendrogram.set_visible(True)
    cg2.ax_row_dendrogram.set_visible(False)
    cg2.ax_col_dendrogram.set_visible(True)

    # create the folder to save clustering results (if it doesn't exist)
    index = sys.argv[1].rfind(".")
    path = sys.argv[1][:index]+".clusters"
    if not os.path.exists(path):
        os.mkdir(path)
    # Save figures
    cg1.savefig('%s/distance_matrix_manhattan.png' %(path), bbox_inches='tight')
    cg2.savefig('%s/distance_matrix_euclidean.png' %(path), bbox_inches='tight')
    #plt.show()
    print("Distance matrices succesfully generated in %s/distance_matrix_{distance type}.png" %(path))

if __name__ == "__main__":
    main()


