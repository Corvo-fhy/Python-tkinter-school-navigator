import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import Menu, Text, Scrollbar
import geopandas as gpd
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import os
from matplotlib.patches import Patch
from matplotlib.backend_bases import MouseEvent
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from shapely.geometry import Point

# 创建主窗口
root = tk.Tk()
root.title("内蒙古财经大学导览系统")
root.geometry("1024x768")

# 设置背景图片
background_image = Image.open("background.jpg")  # 替换为你的背景图片路径
background_photo = ImageTk.PhotoImage(background_image)
background_label = tk.Label(root, image=background_photo)
background_label.place(relwidth=1, relheight=1)

# 创建菜单
menu = Menu(root)
root.config(menu=menu)


def parse_geographic_data():
    # 从 GeoJSON 文件中读取地理数据并解析
    try:
        gdf = gpd.read_file('data.geojson')

        # 分离不同的几何类型
        points = gdf[gdf.geometry.type == 'Point']
        lines = gdf[gdf.geometry.type == 'LineString']
        polygons = gdf[gdf.geometry.type == 'Polygon']

        plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体为黑体
        plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号显示为方块的问题

        # 设置保存文件夹路径
        output_folder = 'output_shapefiles'
        os.makedirs(output_folder, exist_ok=True)  # 创建保存文件夹，如果不存在则创建

        # 设置绘图区域
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))

        # 分别绘制不同几何类型，并设置颜色
        if not points.empty:
            points.plot(ax=ax, marker='o', color='blue', markersize=5, label='Points')
        if not lines.empty:
            lines.plot(ax=ax, color='green', linewidth=2, label='道路')
        if not polygons.empty:
            polygons.plot(ax=ax, edgecolor='k', facecolor='orange', alpha=0.5, label='建筑及学校占地')

        # 手动创建图例并确保颜色正确
        legend_elements = [
            Patch(facecolor='green', edgecolor='black', label='道路'),
            Patch(facecolor='orange', edgecolor='black', alpha=1, label='建筑及学校占地')
        ]

        # 设置图例
        ax.legend(handles=legend_elements, loc='upper left')

        # 设置横纵轴的标签格式为十进制
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: '{:.0f}'.format(val)))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: '{:.0f}'.format(val)))

        # 设置标题
        ax.set_title('基于GeoJSON的内蒙古财经大学可视化地图')
        plt.savefig('map.png')  # 保存为 PNG 格式的文件
        # 显示绘图
        plt.show()

        # 保存为Shapefile文件
        if not points.empty:
            points.to_file(os.path.join(output_folder, 'points_shapefile.shp'), driver='ESRI Shapefile')
        if not lines.empty:
            lines.to_file(os.path.join(output_folder, 'lines_shapefile.shp'), driver='ESRI Shapefile')
        if not polygons.empty:
            polygons.to_file(os.path.join(output_folder, 'polygons_shapefile.shp'), driver='ESRI Shapefile')

        print(f"Shapefiles saved in {output_folder} folder.")

    except Exception as e:
        messagebox.showerror("错误", f"无法解析地理要素: {e}")


def open_shapefile():
    file_path = filedialog.askopenfilename(filetypes=[("Shapefiles", "*.shp")])
    if file_path:
        try:
            gdf = gpd.read_file(file_path)
            display_shapefile_content(gdf)
            messagebox.showinfo("信息", f"已打开 Shapefile 文件: {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开 Shapefile 文件: {e}")


def display_shapefile_content(gdf):
    content_window = tk.Toplevel(root)
    content_window.title("Shapefile 内容")

    text = Text(content_window, wrap="none")
    text.pack(expand=True, fill="both")

    scrollbar_y = Scrollbar(content_window, orient="vertical", command=text.yview)
    scrollbar_y.pack(side="right", fill="y")

    scrollbar_x = Scrollbar(content_window, orient="horizontal", command=text.xview)
    scrollbar_x.pack(side="bottom", fill="x")

    text.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    text.insert("end", gdf.to_string())


def show_school_info():
    info = ("学校简介：\n"
            "占地面积：3000亩\n"
            "在校生人数：20000人\n"
            "学科群：经济学、管理学、法学等")
    messagebox.showinfo("学校信息概况", info)


def show_navigation_map():
    # 创建一个新窗口
    map_window = tk.Toplevel(root)
    map_window.title("导览地图")
    map_window.geometry("800x600")

    # 读取地理数据
    gdf = gpd.read_file('data.geojson')

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体为黑体
    plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号显示为方块的问题

    # 设置绘图区域
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))

    # 绘制地理数据
    gdf.plot(ax=ax, edgecolor='k', facecolor='orange', alpha=0.5)
    ax.set_title('点击地图查看建筑物详情')

    # 设置横纵轴的标签格式为十进制
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: '{:.0f}'.format(val)))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: '{:.0f}'.format(val)))

    # 在Tkinter中显示matplotlib图像
    canvas = FigureCanvasTkAgg(fig, master=map_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

    def on_click(event):
        if isinstance(event, MouseEvent):
            x, y = event.xdata, event.ydata
            if x is not None and y is not None:
                clicked_geom = gdf[gdf.geometry.apply(lambda geom: geom.contains(Point(x, y)))]
                if not clicked_geom.empty:
                    building_info = clicked_geom.iloc[0].to_dict()
                    messagebox.showinfo("建筑物详情", f"建筑物信息: {building_info}")

    fig.canvas.mpl_connect('button_press_event', on_click)


# 添加菜单项
file_menu = Menu(menu, tearoff=0)
menu.add_cascade(label="文件获取", menu=file_menu)
file_menu.add_command(label="解析地理要素", command=parse_geographic_data)
file_menu.add_command(label="打开 Shapefile", command=open_shapefile)

info_menu = Menu(menu, tearoff=0)
menu.add_cascade(label="信息阅览", menu=info_menu)
info_menu.add_command(label="学校信息概况", command=show_school_info)

map_menu = Menu(menu, tearoff=0)
menu.add_cascade(label="学校地图", menu=map_menu)
map_menu.add_command(label="导览地图", command=show_navigation_map)


# 创建按钮
def exit_program():
    root.quit()


def show_images():
    image_window = tk.Toplevel(root)
    image_window.title("特色场景")

    image_paths = ["scene1.jpg", "scene2.jpg", "scene3.jpg"]  # 替换为你的图片路径
    for path in image_paths:
        img = Image.open(path)
        img_photo = ImageTk.PhotoImage(img)
        img_label = tk.Label(image_window, image=img_photo)
        img_label.image = img_photo  # 保持引用
        img_label.pack()


exit_button = tk.Button(root, text="退出", command=exit_program)
exit_button.pack(side=tk.BOTTOM, pady=10)

photo_button = tk.Button(root, text="显示照片", command=show_images)
photo_button.pack(side=tk.BOTTOM, pady=10)

# 运行主循环
root.mainloop()
