import os
import qrcode
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import smtplib
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_qr_code(data):
    """Generate QR code from data"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code to bytes
    img_byte_arr = BytesIO()
    qr_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def send_ticket_confirmation(email, ticket_info, qr_code_data):
    """Send ticket confirmation email with QR code"""
    # Email settings from environment variables
    sender_email = os.getenv('EMAIL_SENDER')
    sender_password = os.getenv('EMAIL_PASSWORD') 
    
    if not sender_email or not sender_password:
        print("Warning: Email credentials not found in environment variables")
        return False
    
    # Create message
    msg = MIMEMultipart()
    msg['Subject'] = f'Xác nhận đặt vé - {ticket_info["event_name"]}'
    msg['From'] = sender_email
    msg['To'] = email
    
    # Email content
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2 style="color: #2c3e50;">Xác nhận đặt vé thành công!</h2>
            <p>Cảm ơn bạn đã đặt vé cho sự kiện của chúng tôi.</p>
            
            <h3 style="color: #2c3e50;">Thông tin vé:</h3>
            <ul>
                <li>Tên sự kiện: {ticket_info['event_name']}</li>
                <li>Mã vé: {ticket_info['ticket_code']}</li>
                <li>Ngày sự kiện: {ticket_info['event_date']}</li>
                <li>Người đặt: {ticket_info['buyer_name']}</li>
            </ul>

            <h3 style="color: #2c3e50;">Quy định và hướng dẫn quan trọng:</h3>
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
                <h4 style="color: #e74c3c;">Quy định về chỗ ngồi:</h4>
                <ul>
                    <li>Chỗ ngồi được sắp xếp theo nguyên tắc "Đến trước, chọn trước" khi check-in tại sự kiện</li>
                    <li>Quý khách vui lòng đến sớm 30-45 phút trước giờ bắt đầu để có nhiều lựa chọn chỗ ngồi tốt</li>
                    <li>Ban tổ chức sẽ hỗ trợ sắp xếp chỗ ngồi cho nhóm đặt vé cùng nhau</li>
                </ul>

                <h4 style="color: #e74c3c;">Quy định check-in:</h4>
                <ul>
                    <li>Vui lòng mang theo mã QR (đính kèm trong email) khi check-in tại sự kiện</li>
                    <li>Check-in bắt đầu 60 phút trước giờ sự kiện</li>
                    <li>Vé không có giá trị khi sự kiện đã bắt đầu quá 15 phút</li>
                </ul>

                <h4 style="color: #e74c3c;">Lưu ý đặc biệt:</h4>
                <ul>
                    <li>Vé đã mua không được đổi hoặc hoàn tiền</li>
                    <li>Mỗi mã QR chỉ được sử dụng một lần duy nhất</li>
                    <li>Không chụp ảnh hoặc chia sẻ mã QR để tránh rủi ro mất vé</li>
                </ul>
            </div>

            <p style="margin-top: 20px;">Vui lòng xuất trình mã QR đính kèm khi tham dự sự kiện.</p>
            
            <p style="color: #7f8c8d;">Nếu bạn có bất kỳ câu hỏi nào, vui lòng liên hệ với chúng tôi qua:</p>
            <ul style="color: #7f8c8d;">
                <li>Email: support@eventservice.com</li>
                <li>Hotline: 1900-xxxx</li>
            </ul>
        </body>
    </html>
    """
    
    # Add HTML content
    msg.attach(MIMEText(html_content, 'html'))
    
    # Generate and attach QR code
    qr_code = generate_qr_code(qr_code_data)
    image = MIMEImage(qr_code)
    image.add_header('Content-ID', '<qr_code>')
    image.add_header('Content-Disposition', 'attachment', filename='ticket_qr.png')
    msg.attach(image)
    
    # Send email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False
