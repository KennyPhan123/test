# PRIMER — Cách đọc `STATE_BRIEF.md`

> Tài liệu này **không chứa dữ liệu save nào** — dùng lại được cho mọi file save.
> Gửi kèm `STATE_BRIEF.md` ở **lượt đầu tiên** cho người/AI chưa biết RimWorld.
> Các lượt sau chỉ cần gửi `STATE_BRIEF.md` (5.4 KB).

---

## 1. RimWorld là gì (30 giây)

Game quản lý thuộc địa trên hành tinh hoang. Bạn điều khiển vài **colonist** sống sót sau tai nạn.

- **Mục tiêu**: giữ họ sống. (Tuỳ cài đặt: xây tàu rời hành tinh, hoặc sống vô hạn.)
- **Storyteller** (Cassandra / Phoebe / Randy) là "AI kể chuyện": định kỳ ném sự kiện vào — raid, bệnh, bão, khách khứa. Độ khó càng cao, sự kiện càng ác.
- **Vòng lặp cốt lõi**: colonist làm việc → tạo ra tài sản → **tài sản càng cao, raid càng mạnh**. Giàu có không phải là an toàn.
- **Thua** khi tất cả colonist chết, mất trí, hoặc bỏ đi. Có 1 người sống là chưa thua.

---

## 2. Thuật ngữ

| Thuật ngữ | Nghĩa |
|---|---|
| **Tick** | Đơn vị thời gian. 2,500 tick = 1 giờ · 60,000 tick = 1 ngày · 3,600,000 tick = 1 năm (60 ngày) |
| **Need (Nhu cầu)** | Thanh 0–100%. Cạn → debuff → có thể **mental break** (phát điên: bỏ việc, phá hoại, bạo lực) |
| **Passion** | ⭐ Minor · ⭐⭐ Major. Lên kỹ năng nhanh hơn, và làm việc đó vui hơn |
| **Skill 0–20** | 0 = rất kém · 10 = khá · 20 = huyền thoại |
| **Blueprint** | Bản vẽ **đã đặt nhưng chưa xây**. Cần: người có `CON` + đủ vật liệu |
| **Bill** | Lệnh sản xuất lặp lại tại một trạm (vd: nấu 10 bữa ăn) |
| **Zone / Area** | Vùng người chơi vẽ: `Stockpile` = nơi cất đồ · `Growing` = ruộng · `Allowed` = giới hạn đi lại |
| **Designation** | Lệnh một lần: đào / chặt cây / săn |
| **Wealth** | Tổng giá trị thuộc địa → **quyết định độ mạnh của raid kế tiếp** |
| **Goodwill** | Quan hệ với phe khác. Âm = thù địch → sẽ raid |
| **Adaptation** | Độ "quen" của storyteller với quy mô colony. Cao = đánh mạnh hơn |

---

## 3. Bảng giải mã 23 loại công việc

Dòng `WORK` trong brief dùng viết tắt. Số = mức ưu tiên (**1 = cao nhất, 3 = thấp**).
**Công việc không được liệt kê = 0 = đang TẮT.**

| Viết tắt | Tên | Làm gì | Kỹ năng |
|---|---|---|---|
| `FF` | Firefighter | Dập lửa | — |
| `PT` | Patient | Tự nằm giường bệnh khi nguy kịch | — |
| `DR` | Doctor | Chữa bệnh, mổ, cho bệnh nhân ăn | Medicine |
| `BR` | BedRest | Nằm dưỡng thương | — |
| `BAS` | Basic | Việc vặt: bật công tắc, mở quan tài, thả tù nhân | — |
| `WRD` | Warden | Quản tù nhân, chiêu mộ | Social |
| `HND` | Handling | Thuần hoá, huấn luyện, vắt sữa, giết mổ thú | Animals |
| `COK` | Cooking | Nấu ăn, mổ thịt | Cooking |
| `HNT` | Hunting | Săn thú — **cần súng** | Shooting |
| `CON` | Construction | Xây, sửa, dỡ, lát nền | Construction |
| `GRW` | Growing | Gieo trồng, thu hoạch | Plants |
| `MIN` | Mining | Đào đá/quặng, khoan sâu | Mining |
| `PC` | PlantCutting | Chặt cây, hái quả dại | Plants |
| `SMI` | Smithing | Rèn vũ khí, gia công | Crafting |
| `TAI` | Tailoring | May quần áo | Crafting |
| `ART` | Art | Tạc tượng, vẽ | Artistic |
| `CRA` | Crafting | Cắt đá, nung, điều chế thuốc | Crafting |
| `HAU` | Hauling | Khuân vác, tiếp tế | — |
| `CLE` | Cleaning | Quét dọn, dọn tuyết | — |
| `RES` | Research | Nghiên cứu | Intellectual |
| `CHI` | Childcare | Chăm trẻ em *(Biotech)* | Social |
| `DKS` | DarkStudy | Nghiên cứu thực thể dị thường *(Anomaly)* | Intellectual |
| `FSH` | Fishing | Câu cá *(Odyssey)* | Animals |

*(Chỉ mục 0–19 là game gốc, 20–22 do DLC. Mod có thể nối thêm ở cuối — khi đó brief sẽ hiện `M23`, `M24`...)*

---

## 4. Ngưỡng — đọc nhanh

| Chỉ số | Tốt | Chú ý | Nguy hiểm |
|---|---|---|---|
| **Mood** | > 70 | 50–70 | **< 35 → mental break** |
| **Food** | > 50 | 30–50 | < 15 (sắp đói) · 0 = chết đói dần |
| **Rest** | > 50 | 30–50 | < 15 (kiệt sức) |
| **Joy** | > 50 | 30–50 | < 15 (dễ phát điên) |

**Sát thương:** máu xấp xỉ theo bộ phận — đầu ~30 · thân ~40 · chân ~40 · tay ~30.
Khi tổng damage trên **một** bộ phận vượt máu của nó → bộ phận bị **phá huỷ** (mất chân/mắt...).
Damage rải trên nhiều bộ phận ít nguy hiểm hơn dồn vào một chỗ.

---

## 5. Cách đọc từng khối trong brief

**Header** — `Y<năm> <mùa> d<ngày> <giờ>h` · `colony <ngày>h` = tuổi thuộc địa ·
`<Tên>/<Độ khó>` = storyteller/độ khó · `weather` = thời tiết hiện tại ·
`raids N` = **đã** xảy ra N cuộc đột kích (là quá khứ, không phải sắp tới).
`Mood TB … ▼` = tâm trạng trung bình đang **giảm** — tín hiệu xấu; `▲` = đang tăng.

**NGƯỜI** — mỗi người một khối: kỹ năng · sức khoẻ · nhu cầu · trang bị · việc đang làm.
`Đang làm: LayDown` = đang nằm (ngủ hoặc dưỡng thương).
`Đang làm: Mine/HaulToCell` = đang làm việc bình thường.
`Khác:` = tước hiệu hoàng gia · ân sủng · psycast · gene — **chỉ hiện khi có**.
*Khi colony > 8 người, brief tự chuyển sang **CHẾ ĐỘ GỌN**: 4 dòng/người thay vì 6.*

**Đọc dòng HP** — đã được phân loại sẵn, **đừng tự đoán**:

| Nhãn | Nghĩa | Đáng lo? |
|---|---|---|
| `N VẾT THƯƠNG (tổng X, M mới)` | tổn thương thật | ⚠️ CÓ — nhất là khi ghi "chưa băng bó" |
| `N cấy ghép/bionic` | chân tay / nội tạng nhân tạo | ✅ TỐT — nâng chỉ số, **không phải bệnh** |
| `N bệnh mãn: …` | hen suyễn, ung thư, đau lưng… | ⚠️ vĩnh viễn, không tự khỏi |
| `N nghiện: …` | nghiện rượu / thuốc… | ⚠️ thiếu chất sẽ phát điên |
| `N tình trạng: …` | cảm cúm, ngộ độc thức ăn, hạ thân nhiệt… | ⚠️ tạm thời, thường tự khỏi |
| `có thai` | đang mang thai | theo dõi |

> Vết thương cũ hơn 3 ngày được gắn `(cũ Nd)` — đó là sẹo đã lành, **không cần băng bó**.

**WORK** — **chỉ liệt kê công việc đang BẬT**. So sánh giữa các colonist để tìm "điểm gãy đơn".

**SCHEDULE** — giờ ngủ (0–23). Còn lại là làm việc.

**COLONY** — `Blueprint: … cần ~200 gỗ, có 0` nghĩa là đã vẽ nhưng chưa xây được.
`Chỉ thị` = lệnh chờ thực hiện. `Kho` = vật liệu hiện có.

**THREATS** — `active=False` = **đang ngủ/yên**, chưa nguy hiểm, nhưng là **nợ sẽ tới** nếu lại gần.

**Điện** — chỉ hiện khi đã xây điện. `sản xuất X W · tiêu thụ Y W`.
`🔴 THIẾU ĐIỆN` nghĩa là X < Y → tủ lạnh, tháp súng, máy nghiên cứu sẽ lần lượt tắt.

**MECH** — robot do thợ cơ khí (mechanitor) điều khiển. Mỗi con tốn **băng thông**; thợ cơ khí chết/ngã = mech ngừng hoạt động.

**NÔ LỆ & TÙ NHÂN** — nô lệ làm việc nhưng **không bị ràng buộc bởi tâm trạng** (vẫn làm khi mood thấp). Tù nhân có **kháng cự** (resistance); phải giảm về 0 mới chiêu mộ được.

**Ý THỨC HỆ** — bộ quy tắc của colony: ăn mặc, ăn uống, nghi lễ. Ví dụ nếu cho phép ăn thịt đồng loại → có nguồn thức ăn khẩn cấp khi đói; nếu ghê tởm nutrient paste → không được dùng máy làm thức ăn rẻ.

**SỰ KIỆN GẦN ĐÂY** — trích từ vết thương: **ai đánh ai, bằng gì, cách đây mấy ngày**. Đây là lịch sử chiến đấu gần nhất, dùng để biết colony vừa trải qua chuyện gì.

**FACTIONS** — 🔴 = thù địch (sẽ raid). ⚪ = trung lập (có thể giao thương).

**⚠ BOTTLENECKS** — quan trọng nhất, đã viết thành câu hoàn chỉnh, người ngoài đọc cũng hiểu.

---

## 6. Nguyên tắc sinh tồn (dùng khi ra quyết định)

Thứ tự ưu tiên kinh điển:

1. **Thức ăn** — chết đói là chắc chắn nhất
2. **Chỗ ở** — ngủ ngoài trời/tuyết = debuff liên tục
3. **Y tế** — vết thương không băng bó → nhiễm trùng → chết
4. **Phòng thủ** — raid đến theo chu kỳ, không tránh được
5. **Nhiên liệu/điện** — cần cho nấu ăn và sưởi/làm mát
6. **Tiện nghi** — bàn ăn, giường riêng, chỗ giải trí (giữ Mood cao)

**Quy tắc vàng về phân công:**
> Đừng để một việc thiết yếu chỉ do đúng **một** người đảm nhiệm. Người đó ốm/bị thương là cả colony tắc.
> Và: nếu **không ai** được gán một việc, mọi chỉ thị liên quan đến việc đó sẽ đứng im vô hạn.

---

## 7. Những điều dễ hiểu sai

| Hiểu sai | Sự thật |
|---|---|
| "Tài sản cao = mạnh" | Tài sản cao → **raid mạnh hơn**. Giàu mà không có phòng thủ = chết |
| "Không có địch trên map = an toàn" | Storyteller sẽ ném raid mới theo chu kỳ |
| "Có đồ ăn trong kho là đủ" | Phải có người **nấu** (bill) và người có `COK` |
| "Cây lớn rồi tự thu hoạch" | Cần người có `GRW`/`PC` |
| "Blueprint đã đặt là sẽ xây" | Cần `CON` + đủ vật liệu tại chỗ |
| "Thú thuần hoá tự sống được" | Thú gặm cỏ cần cỏ; hết cỏ phải cho ăn |
