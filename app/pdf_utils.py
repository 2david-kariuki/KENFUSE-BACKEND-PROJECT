from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas

class PDFGenerator:
    @staticmethod
    def generate_will_pdf(will, user):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        p.setFont("Helvetica-Bold", 20)
        p.drawString(100, 750, "KENFUSE - LAST WILL AND TESTAMENT")
        
        p.setFont("Helvetica", 12)
        p.drawString(100, 700, f"Will Title: {will.title}")
        p.drawString(100, 680, f"Created: {datetime.now().strftime('%Y-%m-%d')}")
        
        p.drawString(100, 650, "Testator Information:")
        p.drawString(120, 630, f"Name: {user.get('first_name', '')} {user.get('last_name', '')}")
        
        if will.get('content'):
            p.drawString(100, 600, "Will Content:")
            content = will.get('content', '')
            y = 580
            lines = content.split('\n')
            for line in lines:
                if y < 50:
                    p.showPage()
                    p.setFont("Helvetica", 12)
                    y = 750
                p.drawString(120, y, line[:80])
                y -= 20
        
        p.setFont("Helvetica-Oblique", 10)
        p.drawString(100, 30, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        p.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def generate_memorial_pdf(memorial_data):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        
        p.setFont("Helvetica-Bold", 24)
        p.drawCentredString(A4[0]/2, 800, "IN MEMORIAM")
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, memorial_data.get('title', 'Memorial'))
        
        p.setFont("Helvetica", 14)
        p.drawString(100, 720, memorial_data.get('name', ''))
        
        y = 690
        if memorial_data.get('birth_date'):
            p.drawString(100, y, f"Born: {memorial_data['birth_date']}")
            y -= 25
        
        if memorial_data.get('death_date'):
            p.drawString(100, y, f"Passed Away: {memorial_data['death_date']}")
            y -= 25
        
        if memorial_data.get('biography'):
            p.setFont("Helvetica-Bold", 14)
            p.drawString(100, y, "Biography:")
            y -= 25
            
            p.setFont("Helvetica", 12)
            bio = memorial_data['biography']
            lines = bio.split('\n')
            for line in lines:
                if y < 50:
                    p.showPage()
                    p.setFont("Helvetica", 12)
                    y = 750
                p.drawString(120, y, line[:80])
                y -= 20
        
        p.setFont("Helvetica-Oblique", 10)
        p.drawString(100, 30, "KENFUSE Memorial")
        p.drawString(100, 15, f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
        
        p.save()
        buffer.seek(0)
        return buffer.getvalue()