"""
This module is used for frequency analysis of hydrological data.
"""

# Libraries

import scipy
import scipy.stats
import matplotlib

from .geo_tools import *

DPI = 200

# Functions

def tests_examples(
        save_path,
):
    """
    
    """
    if not os.path.exists(save_path):
        N = 100
        xlabel = ['(a)', '(b)', '(c)']
        sin = 20 * np.sin(2 * np.pi * np.arange(N) / N)
        data1 = [
            scipy.stats.lognorm.rvs(0.3, 0, 70, N) + sin,
            np.concatenate([
                scipy.stats.lognorm.rvs(0.3, 0, 130, int(N/2)),
                scipy.stats.lognorm.rvs(0.3, 0, 60, int(N/2)),
            ]),
            scipy.stats.lognorm.rvs(0.3, 0, 70, N) + np.arange(N),
        ]
        data2 = [
            sin + 70,
            np.concatenate([
                np.full((int(N/2),), 130),
                np.full((int(N/2),), 60),
            ]),
            np.arange(N) + 70,
        ]
        fig = plt.figure(figsize=(8, 3), dpi=DPI)
        axs = [fig.add_subplot(1, 3, i) for i in range(1, 4)]
        for i, ax in enumerate(axs):
            ax.plot(
                data1[i], lw=0.8, c='black',
            )
            ax.plot(
                data2[i], lw=1.0, c='red',
            )
            ax.grid(alpha=0.5)
            ax.set_axis_off()
        fig.text(0.225, 0, xlabel[0], c='black')
        fig.text(0.500, 0, xlabel[1], c='black')
        fig.text(0.775, 0, xlabel[2], c='black')
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

def map_station_institution(
        bbox, lon, lat, institutions, save_path,
    ):
    """
    Map station's institution.
    """
    if not os.path.exists(save_path):
        institutions = [
            institutions == 'SMN', institutions == 'INA',
            institutions == 'INTA', institutions == 'SNIH',
        ]
        colors = ['red', 'green', 'blue', 'orange']
        mk = 20
        labels = [r'SMN-CIM', r'INA-CIRSA', r'INTA-SIGA', r'RHN-SNIH']
        handles = [
            matplotlib.lines.Line2D(
                [0], [0], linestyle='', marker='o', markeredgecolor='black',
                markeredgewidth=0.2, markerfacecolor=color,
                markersize=mk * 0.25,
            ) for color in colors
        ]
        my_map = Map(bbox=bbox, fontsize=8)
        my_map.create_figure(dpi=DPI)
        my_map.set_map(my_map.ax)
        my_map.ax.add_image(
            cartopy.io.img_tiles.GoogleTiles(style='satellite'), 7
        )
        my_map.draw_limits(
            my_map.ax,
            provinces_shp_path=PROVINCES_SHP_PATH,
            countries_shp_path=COUNTRIES_SHP_PATH,
        )
        my_map.create_north_arrow(my_map.ax)
        for j, inst in enumerate(institutions):
            my_map.ax.scatter(
                lon[inst], lat[inst], c=colors[j], s=mk, zorder=2,
                edgecolors='black', lw=0.2, marker='o',
            )
        my_map.ax.legend(
            handles, labels, loc=(0.65, 0.22), fontsize=my_map.fs,
        )
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

def hist_information(
        institution, lon, lat, elev, for_use, save_path,
    ):
    """
    
    """
    if not os.path.exists(save_path):
        bins = [
            np.arange(-0.5, 4, 1),
            [-76, -72, -68, -64, -60, -56, -52],
            [-56, -50, -44, -38, -32, -26, -20],
            [0, 500, 1000, 1500, 2000, 3000],
        ]
        x_labelticks = copy.deepcopy(bins)
        x_labelticks[0] = np.unique(institution)
        x_ticks = copy.deepcopy(bins)
        x_ticks[0] = np.arange(4)
        x_ticks[-1] = [0, 500, 1000, 1500, 2000, 2500]
        x_lims = copy.deepcopy(x_ticks)
        x_lims[0] = bins[0]
        x_text = copy.deepcopy(bins)
        x_text[-1] = [0, 500, 1000, 1500, 2000, 2500]
        for i, _ in enumerate(x_labelticks[0]):
            institution[institution == _] = i
        institution = institution.astype(int)
        vars = [institution, lon, lat, elev]
        colors = [
            'pink', 'lightblue', 'lightgreen', 'wheat',
        ]
        title = [
            'Fuente de información', 'Longitud',
            'Latitud', 'Elevación (msnm)',
        ]
        fig = plt.figure(figsize=(8, 8), dpi=DPI)
        axs = [fig.add_subplot(2, 2, i) for i in range(1, 5)]
        for i, ax in enumerate(axs):
            vars_ = [vars[i], vars[i][for_use]]
            percentage = list()
            for v, alpha in zip(vars_, [0.5, 1.0]):
                counts, _, _ = ax.hist(
                    v,
                    bins=bins[i],
                    color=colors[i],
                    edgecolor='black',
                    align='mid',
                    alpha=alpha,
                )
                percentage.append(counts)
            percentage = np.array(percentage)
            for j, p in enumerate(percentage.T):
                p_ = 100 * p[1] / p[0]
                ax.text(
                    np.mean([x_text[i][j], x_text[i][j+1]]),
                    5 + p[0],
                    f'{p_:.0f} %', size=8, style='oblique',
                    c='black', rotation=0, ha='center', va='bottom',
                )
            ax.set_title(title[i])
            ax.grid(alpha=0.5, axis='y')
            ax.set_xlim(x_lims[i][0], x_lims[i][-1])
            ax.set_ylim(0, 165)
            ax.set_xticks(x_ticks[i])
            ax.set_xticklabels(x_labelticks[i])
        axs[1].tick_params(labelleft = False)
        axs[3].tick_params(labelleft = False)
        fig.text(
            0.05, 0.5,
            'Cantidad de estaciones',
            va='center', rotation='vertical',
        )
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

def map_start_month(
        bbox, lon, lat, start_month, save_path,
    ):
    """
    Map the start month of the hydrological year.
    """
    if not os.path.exists(save_path):
        colors = [
            '#0000FF', '#007FFF', '#00FFB9',
            '#00FF00', '#80FF00', '#FBFF00',
            '#FF7C00', '#FF0000', '#FF0049',
            '#FF00AE', '#CD00FF', '#7800FF',
        ]
        cmap = matplotlib.colors.ListedColormap(colors)
        bounds = np.arange(0.5, 13, 1)
        my_map = Map(bbox=bbox, fontsize=8)
        my_map.create_figure(dpi=DPI)
        my_map.set_map(my_map.ax)
        my_map.ax.add_image(
            cartopy.io.img_tiles.GoogleTiles(style='satellite'), 7,
        )
        my_map.draw_limits(
            my_map.ax,
            provinces_shp_path=PROVINCES_SHP_PATH,
            countries_shp_path=COUNTRIES_SHP_PATH,
        )
        my_map.create_north_arrow(my_map.ax)
        img = my_map.ax.scatter(
            lon, lat, c=start_month, s=20, cmap=cmap, zorder=2,
            edgecolors='black', lw=0.2,
        )
        cax, kw = matplotlib.colorbar.make_axes(
            my_map.ax, orientation='horizontal', location='bottom',
            fraction=0.15, pad=-0.3, shrink=0.8, aspect=40,
            anchor=(0.46, -1.5), panchor=(0.5, 0.0),
        )
        cb = my_map.fig.colorbar(
            img, cax=cax, boundaries=bounds,
            spacing='uniform', ticks=np.arange(1, 13), **kw
        )
        cb.ax.tick_params(labelsize=my_map.fs)
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

def map_station_test(
        bbox, lon, lat, save_path, cond,
    ):
    """
    Map station's statistical test result.
    """
    if not os.path.exists(save_path):
        colors = ['green', 'blue', 'orange', 'orange', 'red']
        markers = ['o', 'o', '^', 'v', 'o']
        labels = [
            r'Verifica', r'No verifica independencia',
            r'No verifica tendencia (Ascendente)',
            r'No verifica tendencia (Descendente)',
            r'No verifica homogeneidad',
        ]
        handles = [
            matplotlib.lines.Line2D(
                [0], [0], linestyle='', marker=markers[i],
                markeredgecolor='black', markeredgewidth=0.2,
                markerfacecolor=color, markersize=5,
            ) for i, color in enumerate(colors)
        ]
        yes, no_ind, no_trend, _, no_hom = colors
        cond = [
            cond[0]  * cond[1],
            cond[2]  * ~cond[3] * ~cond[4] * ~cond[5] * cond[1], #2
            cond[2]  * cond[3]  * ~cond[4] * ~cond[5] * cond[1], #23
            cond[2]  * ~cond[3] * cond[4]  * ~cond[5] * cond[1], #24
            cond[2]  * ~cond[3] * ~cond[4] * cond[5]  * cond[1], #25
            cond[2]  * cond[3]  * ~cond[4] * cond[5]  * cond[1], #235
            cond[2]  * ~cond[3] * cond[4]  * cond[5]  * cond[1], #245
            ~cond[2] * cond[3]  * ~cond[4] * ~cond[5] * cond[1], #3
            ~cond[2] * cond[3]  * ~cond[4] * cond[5]  * cond[1], #35
            ~cond[2] * ~cond[3] * cond[4]  * ~cond[5] * cond[1], #4
            ~cond[2] * ~cond[3] * cond[4]  * cond[5]  * cond[1], #45
            ~cond[2] * ~cond[3] * ~cond[4] * cond[5]  * cond[1], #5
        ]
        marker = [
            'o', 'o', 'v', '^', 'o', 'v',
            '^', 'v', 'v', '^', '^', 'o',
        ]
        color1 = [
            yes, no_ind, no_ind, no_ind, no_ind, no_ind, no_ind,
            no_trend, no_hom, no_trend, no_hom, no_hom,
        ]
        color2 = [
            None, None, None, None, no_hom, no_hom,
            no_hom, None, None, None, None, None,
        ]
        fillstyle = [
            'full', 'full', 'full', 'full', 'left', 'left',
            'left', 'full', 'full', 'full', 'full', 'full',
        ]
        mk = 5
        my_map = Map(bbox=bbox, fontsize=8)
        my_map.create_figure(dpi=DPI)
        my_map.set_map(my_map.ax)
        my_map.ax.add_image(
            cartopy.io.img_tiles.GoogleTiles(style='satellite'), 7,
        )
        my_map.draw_limits(
            my_map.ax,
            provinces_shp_path=PROVINCES_SHP_PATH,
            countries_shp_path=COUNTRIES_SHP_PATH,
        )
        my_map.create_north_arrow(my_map.ax)
        for i in range(len(cond)):
            if i > 1:
                mk = 5
            my_map.ax.plot(
                lon[cond[i]], lat[cond[i]], zorder=2, marker=marker[i],
                linestyle='', markersize=mk, fillstyle=fillstyle[i],
                markerfacecolor=color1[i], markerfacecoloralt=color2[i],
                markeredgecolor='black', markeredgewidth=0.2,
            )
        my_map.ax.legend(
            handles, labels, loc=(0.50, 0.20), fontsize=my_map.fs,
        )
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

def map_prec(
        bbox, lon_grid, lat_grid, lon, lat, prec, save_path,
        bounds=None, shp_path=None, elevation_mask=None,
        cb_label='Precipitación (mm/día)',
    ):
    """
    
    """
    if not os.path.exists(save_path):
        prec = get_kriging_prec(
            lon, lat, lon_grid, lat_grid, prec, shp_path=shp_path,
            elevation_mask=elevation_mask,
        )
        if bounds is None:
            bounds = np.array([
                0, 10, 20, 30, 40, 50, 60, 80,
                100, 120, 150, 180, 200, 250, 300,
            ])
        colors = [
            '#FFFFFF', '#73B7ED', '#1954FF', '#3AE63A', '#42B842', '#269126',
            '#EFF442', '#F4C942', '#FFAD1D', '#FF3A00', '#D30000', '#BE2222',
            '#7F00D8', '#000000',
        ]
        cmap = matplotlib.colors.ListedColormap(colors)
        norm = matplotlib.colors.BoundaryNorm(
            boundaries=bounds[1:-1], ncolors=len(bounds)-1, extend='both',
        )
        my_map = Map(bbox=bbox, fontsize=8)
        my_map.create_figure(dpi=DPI)
        my_map.set_map(my_map.ax)
        my_map.ax.add_image(
            cartopy.io.img_tiles.GoogleTiles(style='satellite'), 7,
        )
        my_map.draw_limits(
            my_map.ax,
            provinces_shp_path=PROVINCES_SHP_PATH,
            countries_shp_path=COUNTRIES_SHP_PATH,
        )
        my_map.create_north_arrow(my_map.ax)
        my_map.ax.scatter(
            lon, lat, c='red', s=5, zorder=2, edgecolors='black', lw=0.2,
        )
        img = my_map.ax.contourf(
            lon_grid, lat_grid, prec,
            levels=bounds[1:-1], alpha=0.65,
            cmap=cmap, norm=norm, extend='both',
        )
        my_map.ax.contour(
            lon_grid, lat_grid, prec,
            levels=bounds[1:-1], alpha=0.7, norm=norm,
            linewidths=1.2, colors='#576789', extend='both',
        )
        cax, kw = matplotlib.colorbar.make_axes(
            my_map.ax, orientation='horizontal', location='bottom',
            fraction=0.15, pad=-0.3, shrink=0.8, aspect=40,
            anchor=(0.46, -1.5), panchor=(0.5, 0.0),
        )
        cb = my_map.fig.colorbar(
            img, cax=cax, boundaries=bounds,
            spacing='uniform', ticks=bounds[1:-1], **kw
        )
        cb.ax.tick_params(labelsize=my_map.fs)
        cb.set_label(cb_label, fontsize=my_map.fs)
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

def scatter_station_imerg(
        data, data_e, data_l, data_f, name, save_path,
    ):
    """
    
    """
    if not os.path.exists(save_path):
        x = [data_e, data_l, data_f]
        marker = ['s', '^', '.']
        mk = 5
        color = ['pink', 'lightblue', 'lightgreen']
        label = ['IMERG-E', 'IMERG-L', 'IMERG-F']
        fig = plt.figure(figsize=(6, 6), dpi=DPI)
        ax = fig.add_subplot(1, 1, 1)
        ax.plot([0, 100], [0, 100], lw=1, c='black')
        img = [ax.plot(
            x[i], data, zorder=2, marker=marker[i], linestyle='',
            markersize=mk, label=label[i], markerfacecolor=color[i],
            markeredgecolor='black', markeredgewidth=0.2,
        ) for i in range(3)]
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_xlabel('Precipitación Acumulada Diaria de IMERG (mm)')
        ax.set_ylabel(f'Precipitación Acumulada Diaria de "{name}" (mm)')
        ax.grid(alpha=0.5)
        ax.legend(loc=5, ncols=1, shadow=True)
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

def plot_station_imerg(
        dt, data, data_e, data_l, data_f, name, save_path,
    ):
    """
    
    """
    if not os.path.exists(save_path):
        y = [data, data_e, data_l, data_f]
        ls = ['solid', 'dashed', 'dashdot', 'dotted']
        color = ['black', 'red', 'blue', 'green']
        label = [name, 'IMERG-E', 'IMERG-L', 'IMERG-F']
        fig = plt.figure(figsize=(10, 6), dpi=DPI)
        ax = fig.add_subplot(1, 1, 1)
        img = [ax.plot(
            dt, y[i], zorder=2, linestyle=ls[i], lw=1,
            c=color[i], label=label[i],
        ) for i in range(4)]
        ax.set_xlim(
            datetime.datetime(dt[0].year, 1, 1),
            datetime.datetime(dt[-1].year + 1, 1, 1),
        )
        ax.set_ylim(0, 100)
        ax.set_ylabel('Precipitación Acumulada Diaria (mm)')
        ax.grid(alpha=0.5)
        ax.legend(loc=1, ncols=1, shadow=True)
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

def interpolation_method_comparison(
        csv_path, save_path,
    ):
    """
    
    """
    if not os.path.exists(save_path):
        with open(csv_path, 'r', newline='') as csvfile:
            csvreader = csv.reader(csvfile)
            data = [_ for _ in csvreader]
        data_dict = dict()
        while [] in data:
            index = data.index([])
            data_ = data[:index]
            data_dict[data_[0][0]] = np.array(data_[2:], dtype=float)
            data = data[index+1:]
        colors = ['pink', 'lightblue', 'lightgreen']
        handles = [
            matplotlib.patches.Rectangle(
                (0, 0), 1, 1,
                edgecolor='black', lw=0.2, facecolor=c,
            ) for i, c in enumerate(colors)
        ]
        labels = [
            'IMERG-E', 'IMERG-L', 'IMERG-F',
        ]
        positions = np.array([0.1, 0.25, 0.4])
        fig = plt.figure(figsize=(8, 6), dpi=DPI)
        ax = fig.add_subplot(1, 1, 1)
        for i, k_ in enumerate(data_dict.keys()):
            bplot = ax.boxplot(
                [data_dict[k_][:, j] for j in range(data_dict[k_].shape[1])],
                labels=['', k_, ''], positions=positions+i,
                notch=False, vert=True, patch_artist=True,
                medianprops=dict(linewidth=1),
                flierprops=dict(marker='x', alpha=0.2),
            )
            for j, patch in enumerate(bplot['boxes']):
                patch.set_facecolor(colors[j])
        ax.set_xticks(np.arange(positions[1], len(data_dict)))
        ax.set_xticklabels(data_dict.keys())
        ax.set_ylim(0, 160)
        ax.set_ylabel(r'$RMSE\ (mm)$')
        ax.grid(alpha=0.5, axis='y')
        ax.legend(
            handles, labels, loc=2, ncols=1, shadow=True,
        )
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

def map_Catalini_comp(
        bbox, lon_grid, lat_grid, lon, lat,
        prec, confint, save_path,
        Catalini_filepath, Catalini_stations_path,
        bounds=None, shp_path=None, elevation_mask=None,
    ):
    """
    
    """
    vmax = 50
    colors = [
        'black', '#1B4F72', '#2874A6', '#48C9B0', '#76D7C4', '#D1F2EB',
        '#F6DDCC', '#E59866', '#DC7633', '#C0392B', '#922B21', 'black',
    ]
    if not os.path.exists(save_path):
        bounds = np.array([
            -999, -vmax, (-vmax + confint[0])/2, confint[0],
            2*confint[0]/3, confint[0]/3,
            0,
            confint[1]/3, 2*confint[1]/3,
            confint[1], (vmax + confint[1])/2, vmax, 999,
        ])
        cmap = matplotlib.colors.ListedColormap(colors, N=len(colors))
        norm = matplotlib.colors.BoundaryNorm(boundaries=bounds, ncolors=len(colors))
        xc, yc, Zc = open_Catalini(Catalini_filepath)
        interp = scipy.interpolate.RegularGridInterpolator(
            (xc, yc), Zc.T, 'linear', bounds_error=False,
        )
        xc, yc = np.meshgrid(lon_grid, lat_grid)
        Zc = interp(
            np.array([xc.flatten(), yc.flatten()]).T
        ).reshape(yc.shape)
        prec = get_kriging_prec(
            lon, lat, lon_grid, lat_grid, prec,
            shp_path=shp_path, elevation_mask=elevation_mask
        )
        z = 100 * (prec - Zc) / Zc
        lon_c, lat_c = open_stations_Catalini(Catalini_stations_path)
        if bounds is None:
            bounds = np.arange(-vmax, vmax+1, 10)
        my_map = Map(bbox=bbox, fontsize=8)
        my_map.create_figure(dpi=DPI)
        my_map.set_map(my_map.ax)
        my_map.ax.add_image(
            cartopy.io.img_tiles.GoogleTiles(style='satellite'), 7,
        )
        my_map.draw_limits(
            my_map.ax,
            provinces_shp_path=PROVINCES_SHP_PATH,
            countries_shp_path=COUNTRIES_SHP_PATH,
        )
        my_map.create_north_arrow(my_map.ax)
        my_map.ax.scatter(
            lon, lat, c='red', s=5, zorder=2,
            edgecolors='black', lw=0.2,
        )
        my_map.ax.scatter(
            lon_c, lat_c, c='blue', s=5, zorder=2,
            edgecolors='black', lw=0.2,
        )
        img = my_map.ax.contourf(
            lon_grid, lat_grid, z,
            levels=bounds[1:-1],
            alpha=0.65, cmap=cmap, norm=norm,
            extend='neither',
        )
        contour = my_map.ax.contour(
            lon_grid, lat_grid, z,
            levels=bounds, alpha=0.7,
            linewidths=1.2, colors='#576789', extend='neither',
        )
        my_map.ax.clabel(
            contour, bounds[[0, 1, 2, 4, 5, 6, 7, 8, 10, 11, 12]],
            inline=True, fontsize=my_map.fs-3,
        )
        contour = my_map.ax.contour(
            lon_grid, lat_grid, z,
            levels=bounds[[0, 3, 9, 12]], alpha=0.7,
            linewidths=1.2, colors='black', extend='neither',
        )
        my_map.ax.clabel(
            contour, bounds[[3, 9]],
            inline=True, fontsize=my_map.fs-3,
        )
        cax, kw = matplotlib.colorbar.make_axes(
            my_map.ax, orientation='horizontal', location='bottom',
            fraction=0.15, pad=-0.3, shrink=0.8, aspect=40,
            anchor=(0.46, -1.5), panchor=(0.5, 0.0),
        )
        cb = my_map.fig.colorbar(
            img, cax=cax, boundaries=bounds,
            spacing='uniform', ticks=bounds, **kw,
        )
        cb.ax.tick_params(labelsize=my_map.fs)
        cb.set_label('Diferencia (%)', fontsize=my_map.fs)
        labels = [
            r'Estaciones estudiadas',
            r'Estaciones Catalini (2018)',
        ]
        handles = [
            matplotlib.lines.Line2D(
                [0], [0], linestyle='', marker='o',
                markeredgecolor='black', markeredgewidth=0.2,
                markerfacecolor=color, markersize=5,
            ) for color in ['red', 'blue']
        ]
        my_map.ax.legend(
            handles, labels, loc=(0.60, 0.22), fontsize=my_map.fs,
        )
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()
        print(save_path, np.nansum([(z > confint[0]) * (z < confint[1])]) / np.nansum(~np.isnan(z)))

def map_imerg_start_month(
        bbox, lon_grid, lat_grid, sm, save_path, shp_path, elevation_mask
    ):
    """
    
    """
    if not os.path.exists(save_path):
        alpha = 0.7
        sm = sm.astype(float)
        sm = shp_mask(
            sm,
            rasterio.transform.Affine(0.1, 0, lon_grid[0], 0, 0.1, lat_grid[0]),
            shp_path,
        )
        sm = np.ma.masked_array(sm, elevation_mask)
        colors = [
            '#0000FF', '#007FFF', '#00FFB9',
            '#00FF00', '#80FF00', '#FBFF00',
            '#FF7C00', '#FF0000', '#FF0049',
            '#FF00AE', '#CD00FF', '#7800FF',
        ]
        cmap = matplotlib.colors.ListedColormap(colors)
        bounds = np.arange(0.5, 13, 1)
        norm = matplotlib.colors.BoundaryNorm(
            boundaries=bounds, ncolors=len(bounds) - 1, extend='neither',
        )
        my_map = Map(bbox=bbox, fontsize=8)
        my_map.create_figure(dpi=DPI)
        my_map.set_map(my_map.ax)
        my_map.draw_limits(
            my_map.ax,
            provinces_shp_path=PROVINCES_SHP_PATH,
            countries_shp_path=COUNTRIES_SHP_PATH,
        )
        my_map.create_north_arrow(my_map.ax)
        my_map.ax.add_image(
            cartopy.io.img_tiles.GoogleTiles(style='satellite'), 7,
        )
        img = my_map.ax.pcolormesh(
            lon_grid, lat_grid, sm,
            cmap=cmap, norm=norm, alpha=alpha,
        )
        cax, kw = matplotlib.colorbar.make_axes(
            my_map.ax, orientation='horizontal', location='bottom',
            fraction=0.15, pad=-0.3, shrink=0.8, aspect=40,
            anchor=(0.46, -1.5), panchor=(0.5, 0.0),
        )
        cb = my_map.fig.colorbar(
            img, cax=cax, boundaries=bounds,
            spacing='uniform', ticks=np.arange(1, 13), **kw
        )
        cb.ax.tick_params(labelsize=my_map.fs)
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

def map_imerg_test(
        bbox, lon_grid, lat_grid,
        cond_iWW, cond_tMK, cond_hPE,
        save_path, shp_path, elevation_mask,
    ):
    """
    
    """
    if not os.path.exists(save_path):
        result = np.zeros((lat_grid.shape[0], lon_grid.shape[0]))
        result[~cond_iWW * ~cond_hPE * ~cond_tMK] = 1
        result[~cond_iWW *  cond_hPE *  cond_tMK] = 2
        result[ cond_iWW *  cond_hPE * ~cond_tMK] = 3
        result[ cond_iWW * ~cond_hPE *  cond_tMK] = 4
        result[~cond_iWW * ~cond_hPE *  cond_tMK] = 5
        result[~cond_iWW *  cond_hPE * ~cond_tMK] = 6
        result[ cond_iWW * ~cond_hPE * ~cond_tMK] = 7
        result = shp_mask(
            result,
            rasterio.transform.Affine(
                0.1, 0, lon_grid[0], 0, 0.1, lat_grid[0],
            ),
            shp_path,
        )
        result = np.ma.masked_array(result, elevation_mask)
        alpha = 0.7
        bounds = np.arange(-0.5, 7.6, 1)
        colors = [
            'palegreen', 'white', 'red', 'green',
            'blue', 'purple', 'yellow', 'cyan',
        ]
        handles = [
            matplotlib.patches.Rectangle(
                (0, 0), 1, 1,
                edgecolor='black', lw=0.2, facecolor=c,
            ) for i, c in enumerate(colors)
        ]
        labels = [
            'Verifica',
            'No verifica',
            'No verifica independencia',
            'No verifica tendencia',
            'No verifica homogeneidad',
            'No verifica indep./homog.',
            'No verifica indep./tend.',
            'No verifica homog./tend.',
        ]
        labels = [
            f'{100 * np.sum(result == i) / np.sum(~np.isnan(result)):.0f}% {_}'
            for i, _ in enumerate(labels)
        ]
        cmap = matplotlib.colors.ListedColormap(colors)
        norm = matplotlib.colors.BoundaryNorm(
            boundaries=bounds, ncolors=len(bounds) - 1, extend='neither',
        )
        my_map = Map(bbox=bbox, fontsize=8)
        my_map.create_figure(dpi=DPI)
        my_map.set_map(my_map.ax)
        my_map.draw_limits(
            my_map.ax,
            provinces_shp_path=PROVINCES_SHP_PATH,
            countries_shp_path=COUNTRIES_SHP_PATH,
        )
        my_map.create_north_arrow(my_map.ax)
        my_map.ax.add_image(
            cartopy.io.img_tiles.GoogleTiles(style='satellite'), 7,
        )
        my_map.ax.pcolormesh(
            lon_grid, lat_grid, result,
            cmap=cmap, norm=norm, alpha=alpha,
        )
        my_map.ax.legend(
            handles, labels, loc=(0.55, 0.21), ncols=1,
            fontsize=my_map.fs, shadow=True,
            title_fontsize=my_map.fs,
        )
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

def map_imerg_prec(
        bbox, lon_grid, lat_grid, prec, save_path,
        bounds=None, shp_path=None, elevation_mask=None,
        cb_label='Precipitación (mm/día)',
    ):
    """
    
    """
    if not os.path.exists(save_path):
        prec = shp_mask(
            prec,
            rasterio.transform.Affine(
                0.1, 0, lon_grid[0], 0, 0.1, lat_grid[0],
            ),
            shp_path,
        )
        prec = np.ma.masked_array(prec, elevation_mask)
        alpha = 0.7
        if bounds is None:
            bounds = np.array([
                0, 10, 20, 30, 40, 50, 60, 80,
                100, 120, 150, 180, 200, 250, 300,
            ])
        colors = [
            '#FFFFFF', '#73B7ED', '#1954FF', '#3AE63A', '#42B842', '#269126',
            '#EFF442', '#F4C942', '#FFAD1D', '#FF3A00', '#D30000', '#BE2222',
            '#7F00D8', '#000000',
        ]
        cmap = matplotlib.colors.ListedColormap(colors)
        norm = matplotlib.colors.BoundaryNorm(
            boundaries=bounds[1:-1], ncolors=len(bounds)-1, extend='both',
        )
        my_map = Map(bbox=bbox, fontsize=8)
        my_map.create_figure(dpi=DPI)
        my_map.set_map(my_map.ax)
        my_map.ax.add_image(
            cartopy.io.img_tiles.GoogleTiles(style='satellite'), 7,
        )
        my_map.draw_limits(
            my_map.ax,
            provinces_shp_path=PROVINCES_SHP_PATH,
            countries_shp_path=COUNTRIES_SHP_PATH,
        )
        my_map.create_north_arrow(my_map.ax)
        img = my_map.ax.pcolormesh(
            lon_grid, lat_grid, prec,
            cmap=cmap, norm=norm, alpha=alpha,
        )
        cax, kw = matplotlib.colorbar.make_axes(
            my_map.ax, orientation='horizontal', location='bottom',
            fraction=0.15, pad=-0.3, shrink=0.8, aspect=40,
            anchor=(0.46, -1.5), panchor=(0.5, 0.0),
        )
        cb = my_map.fig.colorbar(
            img, cax=cax, boundaries=bounds,
            spacing='uniform', ticks=bounds[1:-1], **kw
        )
        cb.ax.tick_params(labelsize=my_map.fs)
        cb.set_label(cb_label, fontsize=my_map.fs)
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

def map_error(
        bbox, lon, lat, institutions, test, error, save_path,
    ):
    """
    This function maps Error between IMERG and rain gauges.
    """
    def min_index(error):
        if np.all(np.isnan(error)):
            return np.array([True, False, False])
        else:
            return error == np.nanmin(error)
    if not os.path.exists(save_path):
        test = ~test.astype(bool)
        error[test[:, 1], 0, 1] = np.nan
        error[test[:, 2], 1, 1] = np.nan
        error[test[:, 3], 2, 1] = np.nan
        colors = ['red', 'green', 'blue', 'orange']
        markers = ['^', 'o', 's']
        labels = [
            r'SMN', r'INA', r'INTA', r'SNIH',
            r'', r'IMERG-E', r'IMERG-L', r'IMERG-F',
        ]
        aux = mpatches.Rectangle(
            (0, 0), 1, 1, fc='w', fill=False, edgecolor='none', linewidth=0,
        )
        handles = list()
        for j, color in enumerate(colors):
            handles.append(
                matplotlib.lines.Line2D(
                    [0], [0], linestyle='', marker='s',
                    markeredgecolor='black', markeredgewidth=0.2,
                    markerfacecolor=color, markersize=6,
                )
            )
        handles.append(aux)
        for i, marker in enumerate(markers):
            handles.append(
                matplotlib.lines.Line2D(
                    [0], [0], linestyle='', marker=marker,
                    markeredgecolor='black', markeredgewidth=0.2,
                    markerfacecolor='black', markersize=6,
                )
            )
        institutions = [
            institutions == 'SMN', institutions == 'INA',
            institutions == 'INTA', institutions == 'SNIH',
        ]
        my_map = Map(bbox=bbox, fontsize=8)
        my_map.create_figure(dpi=DPI)
        my_map.set_map(my_map.ax)
        my_map.draw_limits(
            my_map.ax,
            provinces_shp_path=PROVINCES_SHP_PATH,
            countries_shp_path=COUNTRIES_SHP_PATH,
        )
        my_map.create_north_arrow(my_map.ax)
        my_map.ax.add_image(
            cartopy.io.img_tiles.GoogleTiles(style='satellite'), 7,
        )
        values_ = np.array([
            np.arange(3)[min_index(error[i, :, 1])][0]
            for i in range(error.shape[0])
        ])
        error_ = np.array([
            error[i, :, 1][min_index(error[i, :, 1])][0]
            for i in range(error.shape[0])
        ])
        for i, marker in enumerate(markers):
            for j, color in enumerate(colors):
                index = (values_ == i) * institutions[j]
                my_map.ax.scatter(
                    lon[index],
                    lat[index],
                    c=color,
                    s=100 * error_[index] / np.nanmax(error_),
                    zorder=2, edgecolors='black', lw=0.2,
                    vmin=0, vmax=2, marker=marker,
                )
        my_map.ax.legend(
            handles, labels, loc=(0.60, 0.21), ncols=2,
            fontsize=my_map.fs, shadow=True,
        )
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()
        
def comp_result(
        stations, for_use, test, save_path,
    ):
    """
    
    """
    if not os.path.exists(save_path):
        T = [2, 5, 10, 25, 50]
        stations = [_ for i, _ in enumerate(stations) if for_use[i]]
        test = test[for_use]
        rain = np.array([
            _[0].result['Y_rx1day']['lognorm'].ppf(T) for _ in stations
        ])
        rain_e = np.array([
            _[1].result['Y_rx1day']['lognorm'].ppf(T)[1] for _ in stations
        ])
        rain_l = np.array([
            _[2].result['Y_rx1day']['lognorm'].ppf(T)[1] for _ in stations
        ])
        rain_f = np.array([
            _[3].result['Y_rx1day']['lognorm'].ppf(T)[1] for _ in stations
        ])
        rain_e[test[:, 1].astype(bool)] = np.nan
        rain_l[test[:, 2].astype(bool)] = np.nan
        rain_f[test[:, 3].astype(bool)] = np.nan
        colors = ['pink', 'lightblue', 'lightgreen']
        labels = [
            'IMERG-E', 'IMERG-L', 'IMERG-F',
            r'Intervalo de confianza $\alpha=0.05$',
        ]
        handles = [
            matplotlib.lines.Line2D(
                [0], [0], linestyle='', marker='s', markeredgecolor='black',
                markeredgewidth=0.2, markerfacecolor=c, markersize=6,
            )
            for c in colors
        ]
        handles.append(matplotlib.lines.Line2D(
            [0], [0], linestyle='--', color='black',
        ))
        x = np.arange(0, len(T), 0.5)
        zeros = np.zeros((x.shape[0]))
        ones = np.ones((x.shape[0]))
        positions = np.array([0.1, 0.25, 0.4])
        fig = plt.figure(figsize=(8, 6), dpi=DPI)
        ax = fig.add_subplot(1, 1, 1)
        for i in range(len(T)):
            scale = rain[:, 2, i] - rain[:, 1, i]
            y = list()
            for _ in [rain_e, rain_l, rain_f]:
                y_ = (_[:, i] - rain[:, 1, i]) / scale
                y.append(y_[~np.isnan(y_)])
            bplot = ax.boxplot(
                y, labels=['', T[i], ''], positions=positions+i, notch=False,
                vert=True, patch_artist=True, medianprops=dict(linewidth=1),
                flierprops=dict(marker='x', alpha=0.2),
            )
            for j, patch in enumerate(bplot['boxes']):
                patch.set_facecolor(colors[j])
        ax.plot(x, ones, linestyle='--', color='black')
        ax.plot(x, zeros, linestyle='-', color='black')
        ax.plot(x, -ones, linestyle='--', color='black')
        ax.set_xticks(np.arange(positions[1], len(T)))
        ax.set_xticklabels(T)
        ax.set_xlabel('Periodo de retorno (años)')
        ax.set_ylabel('Diferencia normalizada entre IMERG y el terreno')
        ax.grid(alpha=0.5, axis='y')
        ax.legend(
            handles, labels, loc=2, ncols=1, shadow=True,
        )
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

def conf_int(
        prec, save_path,
    ):
    """
    
    """
    T = [2, 5, 10, 25, 50]
    data = np.array([
        [
            100 * (prec[:, j, k] - prec[:, 1, k]) / prec[:, 1, k]
            for k in range(prec.shape[2])
        ]
        for j in [2, 0]
    ])
    meds = np.median(data, axis=2)
    if not os.path.exists(save_path):
        colors = ['lightgreen', 'pink']
        handles = [
            matplotlib.patches.Rectangle(
                (0, 0), 1, 1,
                edgecolor='black', lw=0.2, facecolor=c,
            )
            for c in colors
        ]
        labels = [
            'Umbral superior', 'Umbral inferior',
        ]
        fig = plt.figure(figsize=(8, 8), dpi=DPI)
        ax = fig.add_subplot(1, 1, 1)
        for i in range(2):
            bplot = ax.boxplot(
                data[i], labels=T, notch=False,
                vert=True, patch_artist=True,
                medianprops=dict(linewidth=1),
                flierprops=dict(marker='x', alpha=0.2),
            )
            for k, med in enumerate(meds):
                ax.text(
                    k + 1.28, med, f'{med:.0f}',
                    fontsize=8, fontstyle='italic',
                    va='center',
                )
            for patch in bplot['boxes']:
                patch.set_facecolor(colors[i])
        ax.set_xlabel('Periodo de retorno (años)')
        ax.set_ylabel('Diferencia (%)')
        ax.grid(alpha=0.5, axis='y')
        ax.legend(
            handles, labels, loc=2, ncols=1, shadow=True,
            title=r'Intervalo de Confianza',
        )
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()
    return meds

def comp_variables(
        institution, lon, lat, elev, test, error, save_path,
    ):
    """
    
    """
    if not os.path.exists(save_path):
        bins = [
            np.arange(-0.5, 4, 1),
            [-76, -72, -68, -64, -60, -56, -52],
            [-56, -50, -44, -38, -32, -26, -20],
            [0, 500, 1000, 1500, 2000, 3000],
        ]
        x_labelticks = copy.deepcopy(bins)
        x_labelticks[0] = np.unique(institution)
        x_ticks = copy.deepcopy(bins)
        x_ticks[0] = np.arange(4)
        x_ticks[-1] = [0, 500, 1000, 1500, 2000, 2500]
        x_lims = copy.deepcopy(x_ticks)
        x_lims[0] = bins[0]
        for i, _ in enumerate(x_labelticks[0]):
            institution[institution == _] = i
        institution = institution.astype(int)
        vars = [institution, lon, lat, elev]
        title = [
            'Fuente de información', 'Longitud',
            'Latitud', 'Elevación (msnm)',
        ]
        test = ~test.astype(bool)
        error = 100 * error
        error[test[:, 1], 0, 1] = np.nan
        error[test[:, 2], 1, 1] = np.nan
        error[test[:, 3], 2, 1] = np.nan
        x_small = ['IMERG-E', 'IMERG-L', 'IMERG-F']
        colors = ['pink', 'lightblue', 'lightgreen']
        positions = np.array([-0.2, 0.0, 0.2])
        handles = [
            matplotlib.patches.Rectangle(
                (0, 0), 1, 1,
                edgecolor='black', lw=0.2, facecolor=c,
            ) for c in colors
        ]
        cond = [
            [
                ((var >= bins[j][i]) * (var < bins[j][i+1])).astype(bool)
                for i in range(len(bins[j]) - 1)
            ]
            for j, var in enumerate(vars)
        ]
        fig = plt.figure(figsize=(8, 8), dpi=DPI)
        axs = [fig.add_subplot(2, 2, i) for i in range(1, 5)]
        for i, ax in enumerate(axs):
            widths = bins[i][1] - bins[i][0]
            for k, c in enumerate(cond[i]):
                y = [
                    error[:, j, 1][c]
                    for j in range(error.shape[1])
                ]
                y = [
                    y_[~np.isnan(y_)]
                    for y_ in y
                ]
                p = bins[i][k] + (0.5 + positions) * widths
                bplot = ax.boxplot(
                    y, positions=p, notch=False, widths=0.2 * widths,
                    vert=True, patch_artist=True,
                    medianprops=dict(linewidth=0.5),
                    flierprops=dict(marker='x', alpha=0.2),
                )
                for j, patch in enumerate(bplot['boxes']):
                    patch.set_facecolor(colors[j])
                ax.set_title(title[i])
                ax.grid(alpha=0.5, axis='y')
                ax.set_xlim(x_lims[i][0], x_lims[i][-1])
                ax.set_ylim(-5, 105)
                ax.set_xticks(x_ticks[i])
                ax.set_xticklabels(x_labelticks[i])
        axs[1].tick_params(labelleft=False)
        axs[3].tick_params(labelleft=False)
        fig.text(
            0.05, 0.5,
            'Diferencia porcentual absoluta media (%)',
            va='center', rotation='vertical',
        )
        axs[0].legend(
            handles, x_small, loc=2, ncols=1, shadow=True,
        )
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

def pmp_bplot(
        pmp, save_path
):
    """
    
    """
    if not os.path.exists(save_path):
        labels = ['IMERG-E', 'IMERG-L', 'IMERG-F']
        colors = ['pink', 'lightblue', 'lightgreen']
        fig = plt.figure(figsize=(8, 6), dpi=DPI)
        ax = fig.add_subplot(1, 1, 1)
        bplot = ax.boxplot(
            [
                [
                    np.abs(100 * (_[i] - _[0]) / _[0])
                    for _ in pmp
                ]
                for i in range(1, 4)
            ],
            labels=labels, notch=False,
            vert=True, patch_artist=True,
            medianprops=dict(linewidth=1),
            flierprops=dict(marker='x', alpha=0.2),
        )
        for i, patch in enumerate(bplot['boxes']):
            patch.set_facecolor(colors[i])
        ax.grid(alpha=0.5, axis='y')
        ax.set_ylabel('Diferencia porcentual absoluta (%)')
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

def comp_full_station(
        ids: list, save_path, stations, stations_dir, period
):
    """
    
    """
    if not os.path.exists(save_path):
        fs = 12
        ind_k = 'Y_rx1day'
        T = np.arange(2, 51)
        T_ = np.arange(10, 51, 10)
        colors = [
            'black', 'gold', 'red', 'blue', 'green',
        ]
        markers = ['D', 'v', '^', 'o', 's']
        markersize = 3
        handles = [
            matplotlib.lines.Line2D(
                [0], [0], color=colors[i], linestyle='-',
                marker=markers[i],
                markeredgecolor='black', markeredgewidth=0.2,
                markerfacecolor=colors[i], markersize=6,
            )
            for i in range(len(colors))
        ]
        labels = [
            r'Terreno (Serie completa)',
            r'Terreno (Coincidente en el tiempo con IMERG)',
            r'IMERG-E', r'IMERG-L', r'IMERG-F',
        ]
        nrows = int(np.ceil(len(ids) / 2))
        print(nrows, 5 * nrows + 2)
        ncols = 2
        fig = plt.figure(figsize=(4 * ncols + 2, 3 * nrows + 2), dpi=300)
        axs = [fig.add_subplot(nrows, ncols, i) for i in range(1, len(ids) + 1)]
        print(len(axs))
        i = 0
        for _ in stations:
            if _[0].id in ids:
                station = Rain_Gauge()
                station.load(Path(stations_dir, f'{_[0].file}.csv'))
                station.file = _[0].name
                station.period = period
                station.result = dict()
                station.rxDday_calc(1)
                station.sorted_max_calc()
                station = frequency_analysis(station, replace=1)
                print(station.result['Y_rx1day']['data_outliers_tests'])
                axs[i].set_title(
                    f'{station.name}, {station.province} ({station.institution})\nElevación: {int(station.elevation)} msnm',
                    fontsize=fs,
                )
                ln = station.result[ind_k]['lognorm'].ppf(T)
                axs[i].plot(
                    T, ln[0], c=colors[0], ls='--', lw=1,
                )
                axs[i].plot(
                    T, ln[1], c=colors[0], ls='-', lw=1,
                )
                axs[i].plot(
                    T_, station.result[ind_k]['lognorm'].ppf(T_)[1],
                    c=colors[0], ls='',
                    marker=markers[0], markersize=markersize,
                    markeredgecolor='black', markeredgewidth=0.2,
                )
                axs[i].plot(
                    T, ln[2], c=colors[0], ls='--', lw=1,
                )
                for j in range(len(_)):
                    ln = _[j].result[ind_k]['lognorm'].ppf(T)
                    if j == 0:
                        for ci in [0, 2]:
                            axs[i].plot(
                                T, ln[ci], c=colors[j+1], ls='-.', lw=1,
                            )
                    axs[i].plot(
                        T, ln[1], c=colors[j+1], ls='-', lw=1,
                    )
                    axs[i].plot(
                        T_, _[j].result[ind_k]['lognorm'].ppf(T_)[1],
                        c=colors[j+1], ls='',
                        marker=markers[j+1], markersize=markersize,
                        markeredgecolor='black', markeredgewidth=0.2,
                    )
                axs[i].set_xlim(2, 50)
                axs[i].grid(alpha=0.5)
                if i < (nrows-1)*2:
                    axs[i].tick_params(labelbottom=False)
                i += 1
        fig.text(
            0.07, 0.5, 'Precipitación Máxima Diaria Anual (mm)',
            va='center', rotation='vertical', fontsize=fs,
        )
        fig.text(
            0.5, 0.07, 'Periodo de Retorno (años)',
            ha='center', rotation='horizontal', fontsize=fs,
        )
        if i%2 == 0:
            i -= 2
        else:
            i -= 1
        axs[i].legend(
            handles[2:] + handles[:2], labels[2:] + labels[:2],
            loc=(0.50, -0.55), ncols=2, shadow=True,
        )
        fig.subplots_adjust(hspace=0.30, wspace=0.15)
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()