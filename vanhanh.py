import pygame
import random

# --- KHỞI TẠO ---
pygame.init()
CHIEU_RONG, CHIEU_CAO = 1000, 900
man_hinh = pygame.display.set_mode((CHIEU_RONG, CHIEU_CAO))
pygame.display.set_caption("Mô phỏng Đèn Giao Thông Thông Minh - Logic Mệnh Đề")
dong_ho = pygame.time.Clock()

# --- MÀU SẮC ---
TRANG = (255, 255, 255)
DEN = (0, 0, 0)
XAM = (50, 50, 50)
XANH = (0, 255, 100)
DO = (255, 50, 50)
XANH_DUONG = (0, 150, 255)
CO = (34, 139, 34)

# --- THÔNG SỐ GIAO LỘ ---
DO_RONG_DUONG = 220
TAM = CHIEU_RONG // 2
giao_lo = pygame.Rect(TAM - DO_RONG_DUONG // 2, TAM - DO_RONG_DUONG // 2, DO_RONG_DUONG, DO_RONG_DUONG)

# --- TRẠNG THÁI ĐÈN (FSM) ---
den_xanh_hien_tai = "BAC_NAM"
bo_dem_den = 0
THOI_GIAN_CO_BAN = 180 
KHOANG_CACH_AN_TOAN = 40

# ==========================================================
# KIỂM TRA GIAO LỘ CÓ XE KHÁC HƯỚNG KHÔNG
# ==========================================================
def giao_lo_an_toan(huong_xe, danh_sach_xe):
    for xe in danh_sach_xe:
        if xe.lay_rect().colliderect(giao_lo):
            if huong_xe in ["BAC", "NAM"] and xe.huong in ["DONG", "TAY"]:
                return False
            if huong_xe in ["DONG", "TAY"] and xe.huong in ["BAC", "NAM"]:
                return False
    return True

# ==========================================================
# LỚP XE
# ==========================================================
class Xe:
    def __init__(self, huong):
        self.huong = huong
        self.toc_do = 3
        self.kich_thuoc = 20
        
        if huong == "BAC":
            self.x, self.y = TAM - 50, -50
            self.vx, self.vy = 0, self.toc_do
        elif huong == "NAM":
            self.x, self.y = TAM + 30, CHIEU_CAO + 50
            self.vx, self.vy = 0, -self.toc_do
        elif huong == "DONG":
            self.x, self.y = CHIEU_RONG + 50, TAM - 50
            self.vx, self.vy = -self.toc_do, 0
        elif huong == "TAY":
            self.x, self.y = -50, TAM + 30
            self.vx, self.vy = self.toc_do, 0

    def lay_rect(self):
        return pygame.Rect(self.x, self.y, self.kich_thuoc, self.kich_thuoc)

    def duoc_di_chuyen(self, danh_sach_xe):
        rect_hien_tai = self.lay_rect()
        rect_du_kien = pygame.Rect(self.x + self.vx, self.y + self.vy, self.kich_thuoc, self.kich_thuoc)

        # 1. Logic Chống Đâm Xe (Khoảng cách an toàn)
        for xe_khac in danh_sach_xe:
            if xe_khac != self:
                khoang_cach = 0
                if self.huong == "BAC" and xe_khac.huong == "BAC" and xe_khac.y > self.y:
                    khoang_cach = xe_khac.y - self.y
                elif self.huong == "NAM" and xe_khac.huong == "NAM" and xe_khac.y < self.y:
                    khoang_cach = self.y - xe_khac.y
                elif self.huong == "DONG" and xe_khac.huong == "DONG" and xe_khac.x < self.x:
                    khoang_cach = self.x - xe_khac.x
                elif self.huong == "TAY" and xe_khac.huong == "TAY" and xe_khac.x > self.x:
                    khoang_cach = xe_khac.x - self.x
                
                if 0 < khoang_cach < KHOANG_CACH_AN_TOAN:
                    return False

        # 2. Logic Đèn Giao Thông & Giao Lộ
        # Chỉ check khi xe CHƯA vào giao lộ và CHUẨN BỊ đi vào
        if not rect_hien_tai.colliderect(giao_lo):
            if rect_du_kien.colliderect(giao_lo):
                # Check đèn
                if self.huong in ["BAC", "NAM"] and den_xanh_hien_tai != "BAC_NAM":
                    return False
                if self.huong in ["DONG", "TAY"] and den_xanh_hien_tai != "DONG_TAY":
                    return False
                # Check giao lộ trống (Tránh đâm ngang xe đang kẹt trong giao lộ)
                if not giao_lo_an_toan(self.huong, danh_sach_xe):
                    return False
        return True

    def cap_nhat(self, danh_sach_xe):
        if self.duoc_di_chuyen(danh_sach_xe):
            self.x += self.vx
            self.y += self.vy

    def ve(self):
        pygame.draw.rect(man_hinh, XANH_DUONG, self.lay_rect())

# ==========================================================
# CÁC HÀM HỖ TRỢ
# ==========================================================
def dem_xe(danh_sach_xe):
    bn = sum(1 for x in danh_sach_xe if x.huong in ["BAC", "NAM"] and x.y < TAM-110 or x.y > TAM+110)
    dt = sum(1 for x in danh_sach_xe if x.huong in ["DONG", "TAY"] and x.x < TAM-110 or x.x > TAM+110)
    return bn, dt

def cap_nhat_logic_den(so_bn, so_dt):
    global den_xanh_hien_tai, bo_dem_den
    bo_dem_den += 1

    # Logic Toán rời rạc: Tăng thời gian đèn xanh dựa trên số lượng xe đang chờ
    if den_xanh_hien_tai == "BAC_NAM":
        thoi_gian_cho_phep = THOI_GIAN_CO_BAN + (so_bn * 10)
    else:
        thoi_gian_cho_phep = THOI_GIAN_CO_BAN + (so_dt * 10)

    thoi_gian_cho_phep = min(thoi_gian_cho_phep, 600) # Max 10s

    if bo_dem_den >= thoi_gian_cho_phep:
        den_xanh_hien_tai = "DONG_TAY" if den_xanh_hien_tai == "BAC_NAM" else "BAC_NAM"
        bo_dem_den = 0

def ve_ha_tang():
    man_hinh.fill(CO)
    pygame.draw.rect(man_hinh, XAM, (TAM - DO_RONG_DUONG // 2, 0, DO_RONG_DUONG, CHIEU_CAO))
    pygame.draw.rect(man_hinh, XAM, (0, TAM - DO_RONG_DUONG // 2, CHIEU_RONG, DO_RONG_DUONG))
    pygame.draw.line(man_hinh, TRANG, (TAM, 0), (TAM, CHIEU_CAO), 2)
    pygame.draw.line(man_hinh, TRANG, (0, TAM), (CHIEU_RONG, TAM), 2)

def ve_den():
    m_bn = XANH if den_xanh_hien_tai == "BAC_NAM" else DO
    m_dt = XANH if den_xanh_hien_tai == "DONG_TAY" else DO
    vị_tri_den = [
        (TAM - 130, TAM - 130, m_bn), (TAM + 130, TAM - 130, m_dt),
        (TAM - 130, TAM + 130, m_dt), (TAM + 130, TAM + 130, m_bn)
    ]
    for vx, vy, mau in vị_tri_den:
        pygame.draw.circle(man_hinh, DEN, (vx, vy), 22)
        pygame.draw.circle(man_hinh, mau, (vx, vy), 18)

# --- MAIN LOOP ---
def main():
    global bo_dem_den
    danh_sach_xe = []
    bo_dem_spawn = 0
    font = pygame.font.SysFont("Consolas", 20)
    
    dang_chay = True
    while dang_chay:
        ve_ha_tang()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                dang_chay = False

        bo_dem_spawn += 1
        if bo_dem_spawn > 25: 
            huong_moi = random.choice(["BAC", "NAM", "DONG", "TAY"])
            xe_moi = Xe(huong_moi)
            if not any(xe_moi.lay_rect().colliderect(x.lay_rect()) for x in danh_sach_xe):
                danh_sach_xe.append(xe_moi)
            bo_dem_spawn = 0

        so_bn, so_dt = dem_xe(danh_sach_xe)
        cap_nhat_logic_den(so_bn, so_dt)
        
        for xe in danh_sach_xe:
            xe.cap_nhat(danh_sach_xe)
            xe.ve()

        danh_sach_xe = [x for x in danh_sach_xe if -100 < x.x < CHIEU_RONG + 100 and -100 < x.y < CHIEU_CAO + 100]

        ve_den()
        A, B = (so_bn > so_dt), (so_dt > so_bn)
        info = [
            f"XE BN DANG CHO: {so_bn}", f"XE DT DANG CHO: {so_dt}",
            f"MENH DE A (BN > DT): {A}", f"MENH DE B (DT > BN): {B}",
            f"DEN HIEN TAI: {den_xanh_hien_tai}", f"TIMER: {bo_dem_den}"
        ]
        for i, text in enumerate(info):
            man_hinh.blit(font.render(text, True, TRANG), (20, 20 + i * 25))

        pygame.display.flip()
        dong_ho.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()