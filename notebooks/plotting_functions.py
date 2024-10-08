from typing import Callable
import matplotlib.pyplot as plt
from matplotlib import gridspec
import matplotlib as mpl

from madas.plotting import sub_numbers

class IdColorMap():
    """Maps a string to a matplotlib color"""
    
    def __init__(self, 
                 ids=[], 
                 color_map_name: str=None, 
                 key=None, 
                 order=None):
        """
        ids: `Iterable`
        color_map: `mpl.cmap`
        key: `func`
        order: `List[int]`
        """
        if order is None:
            self._ids = sorted(ids, key=key)
        else:
            assert len(order)==len(ids), "Must provide as many ordering variables as values"
            self._ids = [x[0] for x in sorted(zip(order, ids, key=lambda x: x[0]))]
        self._cmap = plt.get_cmap(color_map_name)
        self._sort_key = key
        
    @property
    def color_map(self):
        return self._cmap
    
    @property
    def ids(self):
        return self._ids
    
    def __len__(self):
        return len(self._ids)
    
    def __getitem__(self, id_):
        assert id_ in self.ids, "This id is not registed. Please provide upon initialization."
        color_value = self.ids.index(id_) / (len(self) - 1)
        return self.color_map(color_value)
    
    def __call__(self, id_):
        return self[id_]

def remove_spines(left = False, right = False, spines = False):
    ax = plt.gca()
    plt.setp(ax.spines.values(), visible=spines) # remove outer spines
    ax.tick_params(left=left, labelleft=left)
    ax.tick_params(bottom=right, labelbottom=right)

def mid_to_label(mid):
    return sub_numbers(mid.split("-")[0])

def fingerprint_tuning_comparison_plot(get_dos_value: Callable, 
                                       ssc: object, 
                                       all_mids: list, 
                                       ref_mid: str,
                                       PLU2_most_similar_mids: list,
                                       MIN2_most_similar_mids: list,
                                       filename: str | None = "FingerprintTuning.svg",
                                       show: bool = True):
    colors = IdColorMap(all_mids, color_map_name="Set2")
    outer_figure = plt.figure(figsize = (15,8))
    outer_axes = plt.gca()
    plt.setp(outer_axes.spines.values(), visible=False) # remove outer spines
    outer_axes.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    gs = gridspec.GridSpec(1, 5, figure=outer_figure, wspace = 0.1, hspace = 0)
    gs2 = gridspec.GridSpecFromSubplotSpec(2,1,gs[:3], hspace=0)
    ax_right = outer_figure.add_subplot(gs[3:])
    for mid in all_mids:
        plt.plot(*ssc(*get_dos_value('ZrTe2-f7ad606317e6'), *get_dos_value(mid)), label=mid_to_label(mid), color=colors(mid))
    plt.ylim(0,1)
    plt.xlim(-3,3)
    plt.xlabel("E$_\mathrm{ref}$ [eV]")
    plt.ylabel(f"Similarity to {sub_numbers('ZrTe2')}", labelpad=20)
    ax_right.tick_params(axis='y', which='both', labelleft='off', labelright='on')
    ax_right.yaxis.set_label_position("right")
    ax_right.yaxis.tick_right()
    legend = plt.legend(fontsize=25, frameon=False, loc="lower left")
    for handle in legend.legend_handles:
        handle.set_linewidth(5.0)

    ax_left = outer_figure.add_subplot(gs[:3])
    remove_spines()
    outer_figure.add_subplot(gs2[0])
    plt.plot(*get_dos_value(ref_mid), color=colors(ref_mid), label=mid_to_label(ref_mid))
    for mid in PLU2_most_similar_mids:
        plt.plot(*get_dos_value(mid), color=colors(mid), label=mid_to_label(mid))
    plt.xlim(-3,3)
    plt.ylim(0,2)
    remove_spines(left=True, spines=True)
    outer_figure.add_subplot(gs2[1])
    plt.plot(*get_dos_value(ref_mid), color=colors(ref_mid), label=mid_to_label(ref_mid))
    for mid in MIN2_most_similar_mids:
        plt.plot(*get_dos_value(mid), color=colors(mid), label=mid_to_label(mid))
    plt.xlim(-3,3)
    plt.ylim(0,2)
    y_ticks_, y_ticklabels_ = plt.yticks()
    plt.yticks(ticks = y_ticks_[:-1], labels = map(str, y_ticks_[:-1]))
    plt.xlabel("Energy [eV]")
    ax_left.set_ylabel('DOS [eV/states/Å$^2$]', labelpad=60)
    if filename is not None:
        plt.savefig(filename, format="svg")
    if show:
        plt.show()

def similarity_kpoint_nfunc_plot(similartiy_matrix: object, 
                                 kpoints: list, 
                                 nfunc: list, 
                                 filename: str | None = "AlGaO3_convergence.svg",
                                 show: bool = True, cmap="viridis") -> None:
    ROWS=1000
    outer_figure = plt.figure(figsize = (13,14))
    outer_axes = plt.gca()
    plt.setp(outer_axes.spines.values(), visible=False) # remove outer spines
    outer_axes.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    gs = gridspec.GridSpec(ROWS, 50, figure=outer_figure, wspace = 0, hspace = 0)
    outer_figure.add_subplot(gs[:int(ROWS*4/5),:])
    plt.imshow(similartiy_matrix, interpolation="none", aspect="equal", cmap=cmap)
    plt.grid()
    cbar = plt.colorbar()
    cbar.set_label("Similarity coefficient")
    plt.ylabel("Calculation index")
    plt.xticks(range(0,len(similartiy_matrix),20))
    remove_spines(spines=True, left=True)
    plt.xlim(0,len(similartiy_matrix))
    plt.ylim(0,len(similartiy_matrix))
    matax = plt.gca()
    outer_figure.add_subplot(gs[int(ROWS*4/5):ROWS,:40], sharex=matax)
    plt.xlim(0,len(kpoints)-1)
    plt.plot(kpoints, label="N$_\mathrm{kpt}$")
    plt.plot(range(len(kpoints)),nfunc,label="N$_\mathrm{func}$")
    plt.grid()
    plt.clim(0,1)
    plt.yscale("log")
    plt.xlabel("Calculation index")
    plt.legend(fontsize=24, frameon=True, handlelength=1, fancybox=False, edgecolor="k")
    if filename is not None:
        plt.savefig(filename, format='svg', dpi=200)
    if show:
        plt.show()

def plot_clustered_similarity_matrices_comparison(clus_first: object, 
                                                  clus_second: object, 
                                                  clus_third: object,
                                                  filename: str | None = "AITools.svg",
                                                  show: bool = True, cmap="viridis") -> None:
    """
    Plot three clustered similarity matrices in a 3x3 grid. 
    """

    def plot_similarity_matrix(matrix):
        plt.imshow(matrix, interpolation='none', cmap=cmap)
        plt.xlim(0,len(matrix)-1)
        plt.ylim(0,len(matrix)-1)

    mids_sorted_by_first_clusters = clus_first.get_mids_sorted_by_cluster_labels()
    mids_sorted_by_second_clusters = clus_second.get_mids_sorted_by_cluster_labels()
    mids_sorted_by_third_clusters = clus_third.get_mids_sorted_by_cluster_labels()

    outer_figure = plt.figure(figsize = (14,14))
    outer_axes = plt.gca()
    plt.setp(outer_axes.spines.values(), visible=False) # remove outer spines
    outer_axes.tick_params(left=False, labelleft=False)
    outer_axes.tick_params(bottom=False, labelbottom=False)
    gs = gridspec.GridSpec(3, 3, figure=outer_figure, wspace = 0.005, hspace = 0.05)

    # first SORTED BY first
    outer_figure.add_subplot(gs[0])
    plot_similarity_matrix(clus_first.simat.get_sub_matrix(mids_sorted_by_first_clusters))
    plt.title(f"{clus_first.simat.fp_name} similarity", pad=20, fontsize=30)
    plt.ylabel(f"Sorting:\n{clus_first.simat.fp_name} clusters", fontsize=30)
    plt.gca().tick_params(bottom=False, labelbottom=False)
    plt.gca().ticklabel_format(style="scientific", scilimits=(0,0), axis="y", useMathText=True)

    # second SORTED BY first
    outer_figure.add_subplot(gs[1])
    plot_similarity_matrix(clus_second.simat.get_sub_matrix(mids_sorted_by_first_clusters))
    plt.title(f"{clus_second.simat.fp_name} similarity", pad=46, fontsize=30)
    plt.gca().tick_params(bottom=False, labelbottom=False)
    plt.gca().tick_params(left=False, labelleft=False)

    # third SORTED BY first
    outer_figure.add_subplot(gs[2])
    plot_similarity_matrix(clus_third.simat.get_sub_matrix(mids_sorted_by_first_clusters))
    plt.title(f"{clus_third.simat.fp_name} similarity", pad=46, fontsize=30)
    plt.gca().tick_params(bottom=False, labelbottom=False)
    plt.gca().tick_params(left=False, labelleft=False)


    # first SORTED BY second
    outer_figure.add_subplot(gs[3])
    plot_similarity_matrix(clus_first.simat.get_sub_matrix(mids_sorted_by_second_clusters))
    plt.gca().tick_params(bottom=False, labelbottom=False)
    plt.ylabel(f"Sorting:\n{clus_second.simat.fp_name} clusters", fontsize=30)
    plt.yticks(range(0,4000,1000), map(str, range(0,4,1)))

    # second SORTED BY second
    outer_figure.add_subplot(gs[4])
    plot_similarity_matrix(clus_second.simat.get_sub_matrix(mids_sorted_by_second_clusters))
    plt.gca().tick_params(left=False, labelleft=False)
    plt.gca().tick_params(bottom=False, labelbottom=False)

    # third SORTED BY second
    outer_figure.add_subplot(gs[5])
    plot_similarity_matrix(clus_third.simat.get_sub_matrix(mids_sorted_by_second_clusters))
    plt.gca().tick_params(bottom=False, labelbottom=False)
    plt.gca().tick_params(left=False, labelleft=False)
        
    # first SORTED BY third
    outer_figure.add_subplot(gs[6])
    plot_similarity_matrix(clus_first.simat.get_sub_matrix(mids_sorted_by_third_clusters))
    plt.ylabel(f"Sorting:\n{clus_third.simat.fp_name} clusters", fontsize=30)
    plt.yticks(range(0,4000,1000), map(str, range(0,4,1)))

    # second SORTED BY third
    outer_figure.add_subplot(gs[7])
    plt.gca().tick_params(left=False, labelleft=False)
    plot_similarity_matrix(clus_second.simat.get_sub_matrix(mids_sorted_by_third_clusters))
    plt.xlabel("Material index", fontsize=30)

    # third SORTED BY third
    outer_figure.add_subplot(gs[8])
    plt.gca().tick_params(left=False, labelleft=False)
    plot_similarity_matrix(clus_third.simat.get_sub_matrix(mids_sorted_by_third_clusters))

    # COLORBAR
    cbar_ax = outer_axes.inset_axes([1.02, 0, 0.02, 1])
    norm = mpl.colors.Normalize(vmin=0, vmax=1)
    cb1 = mpl.colorbar.ColorbarBase(cbar_ax, norm=norm, orientation='vertical', cmap=cmap)
    cb1.set_label('Similarity coefficient')
    if filename is not None:
        plt.savefig(filename, format='svg', dpi=200)
    if show:
        plt.show()
