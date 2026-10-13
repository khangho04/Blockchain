# P2P Energy Trading — IoT, AI và Blockchain

Mô hình thử nghiệm giao dịch điện mặt trời ngang hàng (Peer-to-Peer Energy Trading), tích hợp mô phỏng IoT, truyền dữ liệu MQTT, dự đoán năng lượng bằng AI và ghi nhận giao dịch bằng Smart Contract trên Blockchain.

> \*\*Phạm vi demo:\*\* Dự án hiện chạy với dữ liệu năng lượng mô phỏng và mạng Hardhat cục bộ. Token `ENG` là token thử nghiệm, không phải tiền thật. Giao dịch thành công trên Blockchain không đồng nghĩa điện năng đã được truyền tải ngoài thực tế.

## 1\. Kiến trúc tổng quan

```text
IoT Simulator
     │
     ▼
MQTT Publisher ──► Mosquitto Broker ──► Backend / Data Processing
                                           │
                                           ▼
                                      AI Prediction
                                           │
                                           ▼
                                  P2P Market / Matching
                                           │
                                           ▼
                                Smart Contracts (Hardhat)
                                  ├── EnergyToken (ENG)
                                  └── EnergyTrading
                                           │
                                           ▼
                                     Dashboard
```

* **IoT Simulator:** tạo dữ liệu cho các hộ A, B và C.
* **MQTT / Mosquitto:** truyền và nhận dữ liệu.
* **AI:** dự đoán sản lượng điện, mức tiêu thụ và lượng điện dư/thiếu.
* **P2P Market:** xác định bên mua, bên bán và mô phỏng ghép cặp.
* **Blockchain:** dùng Hardhat cục bộ để triển khai và kiểm thử hợp đồng thông minh.
* **Dashboard:** hiển thị thông tin hệ thống bằng Streamlit.

## 2\. Cấu trúc thư mục

Các thư mục chính của dự án:
P2P\_Energy\_Trading/
├── AI\_model/
├── backend/
├── blockchain/
├── data/
├── integration/
├── iot\_code/
├── market/
├── dashboard.py
└── dataset.csv

Một số module được chạy bằng lệnh Python dạng `python -m ...`, vì vậy hãy mở terminal tại thư mục gốc `C:\\P2P\_Energy\_Trading` khi chạy các lệnh tương ứng.

## 3\. Yêu cầu môi trường

Cài đặt các công cụ sau trước khi chạy demo:

* **Python 3** — chạy IoT Simulator, Backend, AI và Dashboard.
* **Node.js và npm** — chạy Hardhat và triển khai Smart Contract.
* **Mosquitto MQTT Broker** — truyền dữ liệu MQTT.
* **Git (không bắt buộc)** — nếu cần lấy mã nguồn từ kho Git.

Kiểm tra các công cụ trong Command Prompt:
python --version
node --version
npm --version
mosquitto -h

Nếu một lệnh không được nhận diện, hãy cài đặt công cụ tương ứng và kiểm tra lại `PATH`.

## 4\. Cài đặt dự án

4.1. Mở thư mục dự án
cd C:\\P2P\_Energy\_Trading


### 4.2. Tạo và kích hoạt môi trường Python ảo (khuyến nghị)

cmd
python -m venv .venv
.venv\\Scripts\\activate



Cài các thư viện Python mà dự án sử dụng. Tùy theo các module có trong mã nguồn, các thư viện thường cần có gồm:

```cmd
pip install pandas numpy scikit-learn joblib paho-mqtt web3 streamlit
```

Nếu dự án đã có `requirements.txt`, ưu tiên cài theo tệp đó:

```cmd
pip install -r requirements.txt
```

### 4.3. Cài đặt Blockchain

```cmd
cd C:\\P2P\_Energy\_Trading\\blockchain
npm install
```

Kiểm tra các script được khai báo trong `package.json`:

```cmd
npm run
```

Lệnh triển khai bên dưới giả định `package.json` có script `deploy` như trong môi trường demo.

## 5\. Cấu hình môi trường

### 5.1. MQTT

Demo sử dụng MQTT Broker trên máy cục bộ, thông thường tại:

```
Host: localhost
Port: 1883
```

Publisher và Backend phải sử dụng cùng địa chỉ Broker và cùng topic theo cấu hình trong mã nguồn.

Khởi động Broker bằng:

```cmd
mosquitto -v
```

Nếu xuất hiện lỗi cho biết không thể sử dụng cổng `1883` vì địa chỉ đã được sử dụng, có thể một tiến trình Mosquitto khác đang chạy. Hãy kiểm tra tiến trình/dịch vụ hiện tại và xác nhận Broker đang hoạt động; không cần khởi chạy thêm một Broker trên cùng cổng. Nếu Broker chưa hoạt động, hãy giải phóng cổng hoặc điều chỉnh cấu hình.

### 5.2. Blockchain cục bộ

Mạng Hardhat cục bộ dùng Chain ID:
31337


Địa chỉ hợp đồng được tạo khi triển khai. Mỗi lần khởi động lại Hardhat node, trạng thái mạng cục bộ có thể bị đặt lại; khi đó cần triển khai lại hợp đồng và cập nhật địa chỉ trong các module sử dụng chúng.

**Địa chỉ đã ghi nhận ở một lần triển khai trước (chỉ dùng nếu đúng với lần chạy hiện tại):**

```
EnergyToken:   0x5FbDB2315678afecb367f032d93F642f64180aa3
EnergyTrading: 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
```

Không sử dụng các địa chỉ này mặc định sau khi khởi động lại node. Hãy lấy địa chỉ mới từ kết quả triển khai và đối chiếu với cấu hình của Backend/Integration.

### 5.3. AI và dữ liệu

Các model đã huấn luyện cần tồn tại tại đúng đường dẫn mà mã nguồn đang tham chiếu. Trong cấu trúc demo đã sử dụng, các tệp model có dạng:

```
AI\_model/models/production\_model.pkl
AI\_model/models/consumption\_model.pkl
```

Tên thư mục và tên tệp có thể khác theo mã nguồn thực tế. Hãy đối chiếu đường dẫn trong mã nguồn. Nếu model chưa được tạo, cần tạo dataset và huấn luyện model trước khi chạy bước dự đoán hoặc tích hợp.

## 6\. Chạy demo

**Mở các cửa sổ terminal riêng** cho những tiến trình cần chạy đồng thời. Giữ các tiến trình nền hoạt động trong suốt quá trình demo.

### Bước 1 — Khởi động Hardhat node

Terminal 1:

```cmd
cd C:\\P2P\_Energy\_Trading\\blockchain
npx hardhat node
```

Giữ terminal này mở. Node cung cấp Blockchain cục bộ và các tài khoản thử nghiệm.

### Bước 2 — Triển khai Smart Contract

Terminal 2:

```cmd
cd C:\\P2P\_Energy\_Trading\\blockchain
npm run deploy
```

Ghi lại địa chỉ `EnergyToken` và `EnergyTrading` được in ra. Đảm bảo các module cần tương tác với hợp đồng đang sử dụng đúng địa chỉ của lần triển khai này.

### Bước 3 — Kiểm tra MQTT Broker

Terminal 3, nếu chưa có Broker hoạt động:

```cmd
mosquitto -v
```

Nếu Broker đã chạy trên cổng `1883`, hãy sử dụng tiến trình hiện có thay vì chạy thêm một bản sao.

### Bước 4 — Khởi động Backend nhận dữ liệu

Terminal 4:

```cmd
cd C:\\P2P\_Energy\_Trading
python -m backend.mqtt\_receiver
```

Kiểm tra log để xác nhận Backend kết nối được tới Broker và nhận dữ liệu. Nếu không có dữ liệu, kiểm tra địa chỉ Broker, topic MQTT và trạng thái Publisher.

### Bước 5 — Chạy IoT Simulator / Publisher

Terminal 5:

```cmd
cd C:\\P2P\_Energy\_Trading
python -m iot\_code.Simulator.mqtt\_publisher
```

Chương trình mô phỏng dữ liệu cho các hộ A, B và C rồi gửi dữ liệu qua MQTT. Kiểm tra log Publisher và Backend để xác nhận dữ liệu được phát và nhận.

### Bước 6 — Chạy luồng tích hợp end-to-end

Mở terminal riêng:

```cmd
cd C:\\P2P\_Energy\_Trading
python -m integration.end\_to\_end
```

Quan sát kết quả dự đoán sản lượng, tiêu thụ, surplus, trạng thái SELLER/BUYER và thông tin giao dịch. Khi giao dịch được thực thi, kiểm tra trạng thái transaction và dữ liệu giao dịch mà hợp đồng thông minh trả về.

> Nếu Publisher chạy liên tục và giữ terminal bận, hãy để Publisher chạy ở terminal riêng. Chỉ dừng Publisher khi đã thu đủ dữ liệu cần thiết và mã tích hợp không còn cần nhận dữ liệu mới.

### Bước 7 — Mở Dashboard

Mở một terminal riêng:

```cmd
cd C:\\P2P\_Energy\_Trading
python -m streamlit run dashboard.py
```

Mở URL mà Streamlit in ra trong terminal; thông thường là:

```text
http://localhost:8501
```

Kiểm tra những thông tin Dashboard thực sự hỗ trợ hiển thị, chẳng hạn dữ liệu năng lượng, kết quả dự đoán và trạng thái giao dịch.

## 7. Xử lý lỗi thường gặp

### MQTT không kết nối được

* Kiểm tra Mosquitto Broker có hoạt động không.
* Xác nhận Publisher và Backend cùng dùng host, port và topic.
* Nếu cổng `1883` đã được sử dụng, xác định tiến trình đang chiếm cổng trước khi khởi động Broker mới.

### Không tìm thấy module Python

* Đảm bảo terminal đang ở thư mục gốc dự án.
* Kích hoạt đúng môi trường ảo.
* Cài thư viện còn thiếu bằng `pip install <ten-goi>` hoặc cài từ `requirements.txt` nếu có.

### Không tìm thấy model AI

* Kiểm tra các tệp `.pkl` đã tồn tại chưa.
* Đối chiếu đường dẫn và cách viết tên thư mục trong mã nguồn.
* Chạy bước tạo dữ liệu/huấn luyện nếu model chưa được tạo.

### Giao dịch Blockchain thất bại

* Đảm bảo Hardhat node vẫn chạy.
* Kiểm tra Chain ID, địa chỉ hợp đồng và ABI đang sử dụng.
* Kiểm tra tài khoản, số dư token và allowance nếu hợp đồng yêu cầu.
* Nếu vừa khởi động lại node, triển khai lại hợp đồng và cập nhật địa chỉ mới.

### Dashboard không mở được

* Xem thông báo lỗi trong terminal chạy Streamlit.
* Kiểm tra cổng đang sử dụng và các thư viện phụ thuộc.
* Dùng đúng URL do Streamlit in ra.

## 8. Lưu ý và giới hạn

* Đây là mô hình thử nghiệm; dữ liệu năng lượng được mô phỏng, không phải số đo từ hệ thống điện thực tế.
* Blockchain cục bộ phục vụ kiểm thử hợp đồng thông minh.
* `ENG` là token thử nghiệm, không có giá trị tiền tệ thực tế.
* Giao dịch được ghi nhận trên Blockchain không chứng minh điện năng đã được truyền tải vật lý giữa các hộ.
* Trước khi triển khai thực tế, cần kiểm thử bảo mật hợp đồng, độ chính xác AI, độ ổn định hệ thống và các yêu cầu pháp lý liên quan.

## 9. Tóm tắt thứ tự chạy

1. Khởi động Hardhat node.
2. Triển khai hợp đồng thông minh.
3. Đảm bảo MQTT Broker đang hoạt động.
4. Khởi động Backend nhận dữ liệu.
5. Chạy IoT Publisher.
6. Chạy luồng tích hợp end-to-end.
7. Mở Dashboard để quan sát kết quả.

