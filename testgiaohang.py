import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from itertools import permutations

# 1. Khởi tạo đồ thị và cấu hình dữ liệu
do_thi = nx.Graph()
cac_tram = [0, 1, 2, 3, 4]
do_thi.add_nodes_from(cac_tram)

print("="*50)
print("SƠ ĐỒ GIAO HÀNG TỐI ƯU (TSP - CHU TRÌNH HAMILTON)")
print("="*50)

# Nhập khoảng cách giữa các cặp trạm
for i in range(len(cac_tram)):
    for j in range(i + 1, len(cac_tram)):
        while True:
            try:
                khoang_cach = float(input(f"Nhập khoảng cách từ Trạm {i} đến Trạm {j}: "))
                do_thi.add_edge(i, j, weight=khoang_cach)
                break
            except ValueError:
                print("Lỗi: Vui lòng nhập một con số thực!")

# 2. Thuật toán tìm chu trình Hamilton ngắn nhất 
def giai_toan_tsp(graph, nut_kho):
    cac_nut_khac = [n for n in cac_tram if n != nut_kho]
    lo_trinh_tot_nhat = None
    quang_duong_min = float('inf')
    
    # Thử tất cả các kịch bản lộ trình (Hoán vị)
    for hoan_vi in permutations(cac_nut_khac):
        lo_trinh_hien_tai = [nut_kho] + list(hoan_vi) + [nut_kho]
        tong_chi_phi = 0
        hop_le = True
        #hàm tính tổng chi phí đường đi :))) cứ mỗi luowitj đi từ cạnh a và b có trọng số là bn
        for k in range(len(lo_trinh_hien_tai) - 1):
            u, v = lo_trinh_hien_tai[k], lo_trinh_hien_tai[k+1]
            if graph.has_edge(u, v):
                tong_chi_phi += graph[u][v]['weight']
            else:
                hop_le = False
                break
        
        if hop_le and tong_chi_phi < quang_duong_min:
            quang_duong_min = tong_chi_phi
            lo_trinh_tot_nhat = lo_trinh_hien_tai
            
    return lo_trinh_tot_nhat, quang_duong_min

# Chạy thuật toán xuất phát từ Trạm 0 (Kho tổng)
tram_kho = 0
lo_trinh_vang, tong_km = giai_toan_tsp(do_thi, tram_kho)

print("\n" + "-"*30)
print(f"KẾT QUẢ TỐI ƯU:")
print(f"Lộ trình: {' -> '.join(map(str, lo_trinh_vang))}")
print(f"Tổng quãng đường: {tong_km} km")
print("-"*30)



#k liên quan
# 3. Cấu hình giao diện và Animation
# Sử dụng circular_layout để tạo hình ngũ giác cân đối
vi_tri = nx.circular_layout(do_thi)
fig, ax = plt.subplots(figsize=(8, 6))
fig.canvas.manager.set_window_title('Mô phỏng Giao hàng Thông minh')

def cap_nhat_do_hoa(khung_hinh):
    ax.clear()
    
    # Vẽ toàn bộ mạng lưới giao thông (màu nhạt, nét đứt để tạo chiều sâu)
    nx.draw_networkx_nodes(do_thi, vi_tri, node_color='#ecf0f1', node_size=1200, 
                           edgecolors='#7f8c8d', ax=ax)
    nx.draw_networkx_edges(do_thi, vi_tri, edge_color='#bdc3c7', alpha=0.3, 
                           style='dashed', ax=ax)
    
    # Hiển thị số km trên các cạnh
    nhan_canh = nx.get_edge_attributes(do_thi, 'weight')
    nx.draw_networkx_edge_labels(do_thi, vi_tri, edge_labels=nhan_canh, ax=ax, font_size=9)

    # Xử lý lộ trình đang di chuyển
    duong_da_di = lo_trinh_vang[:khung_hinh + 1]
    canh_dang_di = list(zip(duong_da_di, duong_da_di[1:]))
    
    # Tô màu các trạm đã ghé thăm
    nx.draw_networkx_nodes(do_thi, vi_tri, nodelist=duong_da_di, 
                           node_color='#2ecc71', node_size=1300, ax=ax) # Xanh lá
    
    # Đánh dấu vị trí hiện tại của Shipper
    nx.draw_networkx_nodes(do_thi, vi_tri, nodelist=[lo_trinh_vang[khung_hinh]], 
                           node_color='#e74c3c', node_size=1500, ax=ax) # Đỏ
    
    # Vẽ đường đi chính thức (Màu xanh đậm, nét liền dày)
    if canh_dang_di:
        nx.draw_networkx_edges(do_thi, vi_tri, edgelist=canh_dang_di, 
                               edge_color='#2980b9', width=5, ax=ax)
    
    # Nhãn tên trạm
    nx.draw_networkx_labels(do_thi, vi_tri, font_color='black', font_weight='bold', ax=ax)

    # Thông tin trạng thái
    ax.set_title(f"MÔ PHỎNG LỘ TRÌNH GIAO HÀNG\n"
                 f"Trạng thái: Đang đến Trạm {lo_trinh_vang[khung_hinh]} | Tổng: {tong_km} km", 
                 fontsize=14, color='#2c3e50', fontweight='bold')
    ax.axis('off')

# Tạo hiệu ứng chuyển động
ani = FuncAnimation(fig, cap_nhat_do_hoa, frames=len(lo_trinh_vang), 
                    interval=1200, repeat=True)

plt.tight_layout()
print("\nĐang khởi động giao diện mô phỏng...")
plt.show()