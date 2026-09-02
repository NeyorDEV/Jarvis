import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128

def generate_disney_pdf(filename):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4 # 595.27 x 841.89 pt

    # Colors
    c_navy = colors.HexColor("#1b1432")
    c_gold = colors.HexColor("#d4af37")
    c_pink = colors.HexColor("#d63031")
    c_dark_text = colors.HexColor("#1e293b")
    c_sub_text = colors.HexColor("#64748b")

    def draw_single_ticket(top_y, guest_name, ticket_num):
        ticket_h = 320
        left_x = 35
        t_width = width - 70

        # Outer Frame
        c.setStrokeColor(c_navy)
        c.setLineWidth(1.5)
        c.setFillColor(colors.white)
        c.roundRect(left_x, top_y - ticket_h, t_width, ticket_h, 10, fill=1, stroke=1)

        # Header Banner (Dark Plum Navy)
        header_h = 70
        c.setFillColor(c_navy)
        c.roundRect(left_x, top_y - header_h, t_width, header_h, 10, fill=1, stroke=0)
        c.rect(left_x, top_y - header_h, t_width, 15, fill=1, stroke=0)

        # Gold Line Separator
        c.setFillColor(c_gold)
        c.rect(left_x, top_y - header_h, t_width, 2.5, fill=1, stroke=0)

        # Header Text
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(left_x + 20, top_y - 30, "DISNEYLAND PARIS")

        c.setFillColor(c_gold)
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(left_x + t_width - 20, top_y - 28, "BILLET D'ENTRÉE")

        c.setFillColor(colors.HexColor("#dfe6e9"))
        c.setFont("Helvetica", 9)
        c.drawString(left_x + 20, top_y - 50, "BILLET D'ACCÈS OFFICIEL")
        c.drawRightString(left_x + t_width - 20, top_y - 50, "VALIDITÉ 1 JOUR")

        # Ticket Body
        body_y = top_y - header_h - 20

        # Guest Holder Box
        c.setFillColor(colors.HexColor("#f8fafc"))
        c.setStrokeColor(colors.HexColor("#cbd5e1"))
        c.setLineWidth(0.8)
        c.roundRect(left_x + 20, body_y - 55, t_width - 40, 55, 6, fill=1, stroke=1)

        c.setFillColor(c_sub_text)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(left_x + 35, body_y - 18, "TITULAIRE DU BILLET")
        
        c.setFillColor(c_navy)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(left_x + 35, body_y - 42, guest_name)

        c.setFillColor(c_pink)
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(left_x + t_width - 35, body_y - 34, "ACCÈS OFFICIEL")

        # Invitation Banner
        banner_y = body_y - 75
        c.setFillColor(colors.HexColor("#fffdf0"))
        c.setStrokeColor(c_gold)
        c.setLineWidth(1)
        c.roundRect(left_x + 20, banner_y - 45, t_width - 40, 45, 6, fill=1, stroke=1)

        c.setFillColor(c_dark_text)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(left_x + t_width / 2, banner_y - 20, "✨ ON PART VIVRE LA MAGIE À DISNEYLAND PARIS ! ✨")
        
        c.setFillColor(c_sub_text)
        c.setFont("Helvetica", 9.5)
        c.drawCentredString(left_x + t_width / 2, banner_y - 36, "Présentez ce billet à l'entrée du parc")

        # Bottom Barcode Area (Clean & Modern)
        bar_y = banner_y - 105
        c.setStrokeColor(colors.HexColor("#e2e8f0"))
        c.line(left_x + 20, bar_y + 60, left_x + t_width - 20, bar_y + 60)

        # Draw Clean Centered Barcode
        barcode = code128.Code128(ticket_num, barWidth=1.4, barHeight=36)
        barcode.drawOn(c, left_x + (t_width - 240) / 2, bar_y + 15)

        c.setFillColor(c_dark_text)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawCentredString(left_x + t_width / 2, bar_y + 2, f"BILLET N° {ticket_num}")

    # Draw Ticket 1: Clara ASTIER
    draw_single_ticket(800, "Clara ASTIER", "DNP-2026-8849102-A")

    # Draw Ticket 2: Mylan PERRIER
    draw_single_ticket(430, "Mylan PERRIER", "DNP-2026-8849102-B")

    # Save PDF
    c.save()
    print("PDF BILLETS DISNEY MIS À JOUR AVEC CLARA ASTIER ET MYLAN PERRIER À :", filename)

if __name__ == "__main__":
    output_path = os.path.abspath("backend/sandbox/surprise_disney/assets/billets.pdf")
    generate_disney_pdf(output_path)
