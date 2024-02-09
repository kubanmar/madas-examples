
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.cm import get_cmap

def remove_spines(left = False, right = False, spines = False):
    ax = plt.gca()
    plt.setp(ax.spines.values(), visible=spines) # remove outer spines
    ax.tick_params(left=left, labelleft=left)
    ax.tick_params(bottom=right, labelbottom=right)

#TODO: Add  me!


def similarity_kpoint_nfunc_plot(similartiy_matrix: object, 
                                 kpoints: list, 
                                 nfunc: list, 
                                 filename: str | None = "AlGaO3_convergence.svg",
                                 show: bool = True) -> None:
    ROWS=1000
    outer_figure = plt.figure(figsize = (13,14))
    outer_axes = plt.gca()
    plt.setp(outer_axes.spines.values(), visible=False) # remove outer spines
    outer_axes.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    gs = gridspec.GridSpec(ROWS, 50, figure=outer_figure, wspace = 0, hspace = 0)
    outer_figure.add_subplot(gs[:int(ROWS*4/5),:])
    plt.imshow(similartiy_matrix, interpolation="none", aspect="equal")
    plt.grid()
    cbar = plt.colorbar()
    cbar.set_label("Similarity coefficient")
    plt.ylabel("Calculation index")
    plt.xticks(range(0,150,20))
    remove_spines(spines=True, left=True)
    plt.xlim(0,144)
    plt.ylim(0,144)
    matax = plt.gca()
    outer_figure.add_subplot(gs[int(ROWS*4/5):ROWS,:40], sharex=matax)
    plt.xlim(0,len(kpoints)-1)
    plt.plot(kpoints, label="N$_\mathrm{kpt}$")
    plt.plot(range(len(kpoints)),nfunc,label="N$_\mathrm{func}$")
    plt.grid()
    plt.clim(0,1)
    plt.yscale("log")
    plt.xlabel("Calculation index")
    plt.legend(fontsize=24, frameon=False)
    if filename is not None:
        plt.savefig(filename, format='svg', dpi=200)
    if show:
        plt.show()


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
        self._cmap = get_cmap(color_map_name)
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