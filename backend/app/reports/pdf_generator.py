from __future__ import annotations
import io, os, uuid
from datetime import datetime
from pathlib import Path
from typing import Any
import qrcode
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from app.config import settings

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 18 * mm
PRIMARY = colors.HexColor("#2563EB")
DARK = colors.HexColor("#0F172A")
LIGHT_GRAY = colors.HexColor("#F1F5F9")
SEV_COLORS = {"Minor":colors.HexColor("#22C55E"),"Low":colors.HexColor("#84CC16"),"Moderate":colors.HexColor("#F59E0B"),"High":colors.HexColor("#F97316"),"Critical":colors.HexColor("#EF4444")}

def _st():
    return {
        "SectionHead": ParagraphStyle("SH", fontName="Helvetica-Bold", fontSize=12, textColor=PRIMARY, spaceBefore=8, spaceAfter=4),
        "Body": ParagraphStyle("B", fontName="Helvetica", fontSize=9, textColor=DARK),
        "Small": ParagraphStyle("S", fontName="Helvetica", fontSize=7, textColor=colors.grey),
    }

def _qr_image(data: str) -> io.BytesIO:
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def generate_pdf(inspection: Any, user: Any) -> str:
    report_dir = Path(settings.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = str(report_dir / f"CAPVIA_{inspection.id}.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN, title=f"CAPVIA AI - Inspection Report #{inspection.id}", author="CAPVIA AI Platform")
    st = _st()
    story = []

    # Header
    hd = [[
        Paragraph("<b>CAPVIA AI</b>", ParagraphStyle("H", fontName="Helvetica-Bold", fontSize=20, textColor=colors.white)),
        Paragraph(f"INSPECTION REPORT<br/><font size=8>ID: {inspection.id}</font>", ParagraphStyle("HR", fontName="Helvetica", fontSize=11, textColor=colors.white, alignment=TA_RIGHT)),
    ]]
    ht = Table(hd, colWidths=[PAGE_WIDTH*0.5-MARGIN, PAGE_WIDTH*0.5-MARGIN])
    ht.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),PRIMARY),("PADDING",(0,0),(-1,-1),12),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story.append(ht)
    story.append(Spacer(1, 8*mm))

    # Details
    story.append(Paragraph("Vehicle & Inspection Details", st["SectionHead"]))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY))
    story.append(Spacer(1, 3*mm))
    date_str = inspection.created_at.strftime("%d %B %Y, %I:%M %p")
    details = [["Owner Name", inspection.owner_name or "N/A", "Date", date_str],["Vehicle Number", inspection.vehicle_number, "Model", inspection.vehicle_model or "N/A"],["Inspector", inspection.inspector_name or "N/A", "Severity", inspection.severity_label or "N/A"]]
    dt = Table(details, colWidths=[40*mm,55*mm,40*mm,55*mm])
    dt.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),"Helvetica"),("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9),("ROWBACKGROUNDS",(0,0),(-1,-1),[LIGHT_GRAY,colors.white]),("GRID",(0,0),(-1,-1),0.5,colors.lightgrey),("PADDING",(0,0),(-1,-1),6)]))
    story.append(dt)
    story.append(Spacer(1, 6*mm))

    # Images
    story.append(Paragraph("Inspection Images", st["SectionHead"]))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY))
    story.append(Spacer(1, 3*mm))
    iw = (PAGE_WIDTH - 2*MARGIN - 10*mm) / 2
    ih = iw * 0.65
    img_row = []
    for label, path in [("Original Image", inspection.image_path), ("AI Annotated Image", inspection.result_path)]:
        cell = [Paragraph(f"<b>{label}</b>", ParagraphStyle("IL", fontName="Helvetica-Bold", fontSize=9, alignment=TA_CENTER))]
        if path and os.path.exists(path):
            cell.append(Image(path, width=iw, height=ih))
        else:
            cell.append(Paragraph("[Image not available]", ParagraphStyle("NA", fontName="Helvetica", fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))
        img_row.append(cell)
    it = Table([img_row], colWidths=[iw+2*mm, iw+2*mm])
    it.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("PADDING",(0,0),(-1,-1),4)]))
    story.append(it)
    story.append(Spacer(1, 6*mm))

    # Findings
    story.append(Paragraph("AI Defect Findings", st["SectionHead"]))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY))
    story.append(Spacer(1, 3*mm))
    defects = inspection.defects or []
    if defects:
        fd = [["#","Defect Type","Confidence","Area (mm2)","Length","Width","Glare?"]]
        for i, d in enumerate(defects, 1):
            fd.append([str(i),d.get("class_name","N/A").replace("_"," ").title(),f"{d.get('confidence',0):.1%}",f"{d.get('area_mm2',0):.2f}",f"{d.get('length_mm',0):.2f} mm",f"{d.get('width_mm',0):.2f} mm","Yes" if d.get("is_glare") else "No"])
        ft = Table(fd, colWidths=[8*mm,38*mm,24*mm,24*mm,22*mm,22*mm,16*mm])
        ft.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),PRIMARY),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),("ROWBACKGROUNDS",(0,1),(-1,-1),[LIGHT_GRAY,colors.white]),("GRID",(0,0),(-1,-1),0.4,colors.lightgrey),("PADDING",(0,0),(-1,-1),5)]))
        story.append(ft)
    else:
        story.append(Paragraph("No defects detected. Vehicle surface PASS.", st["Body"]))
    story.append(Spacer(1, 6*mm))

    # Severity + Cost
    story.append(Paragraph("Severity Assessment & Repair Cost", st["SectionHead"]))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY))
    story.append(Spacer(1, 3*mm))
    sev_color = SEV_COLORS.get(inspection.severity_label or "Minor", PRIMARY)
    score = inspection.severity_score or 0.0
    sd = [[
        Paragraph(f'<font color="white"><b>SEVERITY: {inspection.severity_label or "N/A"}</b><br/>Score: {score:.1f}/100<br/>Defects: {inspection.defect_count or 0} | Total Area: {inspection.total_area_mm2 or 0:.2f} mm2</font>', ParagraphStyle("SC", fontName="Helvetica-Bold", fontSize=11, textColor=colors.white)),
        Paragraph(f'<font color="white"><b>Rs. {inspection.repair_cost_estimated or 0:,.0f}</b><br/><font size=8>Range: Rs.{inspection.repair_cost_min or 0:,.0f} - Rs.{inspection.repair_cost_max or 0:,.0f}<br/>Time: {inspection.time_required or "N/A"} | Priority: {inspection.priority or "N/A"}</font></font>', ParagraphStyle("CC", fontName="Helvetica-Bold", fontSize=11, textColor=colors.white, alignment=TA_RIGHT)),
    ]]
    svt = Table(sd, colWidths=[(PAGE_WIDTH-2*MARGIN)/2, (PAGE_WIDTH-2*MARGIN)/2])
    svt.setStyle(TableStyle([("BACKGROUND",(0,0),(0,0),sev_color),("BACKGROUND",(1,0),(1,0),PRIMARY),("PADDING",(0,0),(-1,-1),12),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story.append(svt)
    story.append(Spacer(1, 6*mm))

    # Recommendation
    story.append(Paragraph("Recommendation", st["SectionHead"]))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(inspection.recommendation or "No recommendation.", st["Body"]))
    story.append(Spacer(1, 8*mm))

    # QR + Footer
    qr_buf = _qr_image(f"CAPVIA-INSPECTION:{inspection.id}")
    fd2 = [[
        Image(qr_buf, width=22*mm, height=22*mm),
        Paragraph(f"Scan to verify | ID: {inspection.id}<br/>Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}<br/><font size=6>This report was generated by CAPVIA AI.</font>", ParagraphStyle("F", fontName="Helvetica", fontSize=8, textColor=colors.grey)),
    ]]
    fdt = Table(fd2, colWidths=[28*mm, PAGE_WIDTH-2*MARGIN-28*mm])
    fdt.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("PADDING",(0,0),(-1,-1),4),("LINEABOVE",(0,0),(-1,0),0.5,colors.lightgrey)]))
    story.append(fdt)
    doc.build(story)
    return pdf_path
