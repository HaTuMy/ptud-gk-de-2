# Task Management System

## Thông tin cá nhân  

Họ và tên: Lê Hà Tú My  

Mã số sinh viên : 22648801  
--------------------
- Dự án: Web quản lý công việc (Tasks)
- Mô tả: Một hệ thống quản lý công việc với vai trò người dùng và quản trị viên

## Mô tả dự án
Đây là một hệ thống quản lý tác vụ dựa trên Flask cho phép người dùng:
- Quản lý công việc của mình (Công việc đã hoàn thành, chưa hoàn thành)
- Tải lên hình đại diện
- Phân loại công việc
- Theo dõi thời gian tạo và hoàn thành
- Hỗ trợ hai vai trò người dùng (quản trị viên và người dùng thông thường)

## Tính năng
1. Xác thực người dùng (Vai trò Quản trị viên và Người dùng)
2. Quản lý công việc với các danh mục
3. Hệ thống tải lên hình đại diện
4. Bố cục dựa trên thẻ
5. Thống kê nhiệm vụ

## Installation Instructions

1. Clone the repository:
```bash
git clone https://github.com/HaTuMy/ptud-gk-de-2.git
cd ptud-gk-de-2
```
Cách 1: 
run file ***install.bat*** 


Cách 2: Chạy lệnh sau  
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate



3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the application:
```bash
flask run
```

6. Access the application at: http://localhost:5000

## Technology Stack
- Python 3.x
- Flask
- SQLAlchemy
- HTML/CSS
- SQLite 
