# apps/commandes/pdf_utils.py

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.utils import timezone


def generer_recu_pdf(commande):
    """
    Génère un reçu PDF pour une commande
    
    Args:
        commande: Instance de Commande
        
    Returns:
        BytesIO: Buffer contenant le PDF
    """
    buffer = BytesIO()
    
    # Configuration du document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Style personnalisé pour le titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    
    # Style pour les en-têtes
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=8,
    )
    
    # Style pour le texte normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        alignment=TA_CENTER,

    )
    
    # Style pour les totaux
    total_style = ParagraphStyle(
        'CustomTotal',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#059669'),
        alignment=TA_RIGHT,
        fontName='Helvetica-Bold',
    )
    
    # Éléments du document
    elements = []
    
    # ═══════════════════════════════════════════════════════════
    # EN-TÊTE DU RESTAURANT
    # ═══════════════════════════════════════════════════════════
    
    elements.append(Paragraph('RESTAURANT MANAGER', title_style))
    elements.append(Paragraph('Système de Gestion de Restaurant', normal_style))
    elements.append(Spacer(1, 20))
    
    # Ligne de séparation
    elements.append(Paragraph('─' * 60, normal_style))
    elements.append(Spacer(1, 12))
    
    # ═══════════════════════════════════════════════════════════
    # INFORMATIONS DU REÇU
    # ═══════════════════════════════════════════════════════════
    
    elements.append(Paragraph('<b>REÇU DE COMMANDE</b>', header_style))
    
    # Tableau des informations de commande
    info_data = [
        ['Numéro de commande:', f'#{commande.id}'],
        ['Date:', commande.date_commande.strftime('%d/%m/%Y à %H:%M')],
        ['Table:', commande.table.login],
        ['Statut:', commande.get_statut_display()],
    ]
    
    if commande.serveur_ayant_servi:
        info_data.append(['Servi par:', commande.serveur_ayant_servi.login])
    
    info_table = Table(info_data, colWidths=[120, 300])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # ═══════════════════════════════════════════════════════════
    # DÉTAILS DES PLATS
    # ═══════════════════════════════════════════════════════════
    
    elements.append(Paragraph('<b>DÉTAILS DE LA COMMANDE</b>', header_style))
    elements.append(Spacer(1, 8))
    
    # En-tête du tableau des plats
    plats_data = [
        ['Plat', 'Prix Unit.', 'Qté', 'Total'],
    ]
    
    # Lignes des plats
    for item in commande.items.all():
        plats_data.append([
            item.plat.nom,
            f'{float(item.prix_unitaire):,.0f} GNF',
            str(item.quantite),
            f'{float(item.sous_total):,.0f} GNF',
        ])
    
    # Créer le tableau
    plats_table = Table(plats_data, colWidths=[220, 80, 40, 100])
    plats_table.setStyle(TableStyle([
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        # Corps du tableau
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    
    elements.append(plats_table)
    elements.append(Spacer(1, 20))
    
    # ═══════════════════════════════════════════════════════════
    # TOTAL
    # ═══════════════════════════════════════════════════════════
    
    total_data = [
        ['', '', 'MONTANT TOTAL:', f'{float(commande.montant_total):,.0f} GNF'],
    ]
    
    total_table = Table(total_data, colWidths=[200, 80, 150, 100])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (2, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (2, 0), (-1, 0), colors.white),
        ('ALIGN', (2, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (2, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (2, 0), (-1, 0), 14),
        ('TOPPADDING', (2, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (2, 0), (-1, 0), 12),
    ]))
    
    elements.append(total_table)
    elements.append(Spacer(1, 30))
    
    # ═══════════════════════════════════════════════════════════
    # INFORMATIONS DE PAIEMENT
    # ═══════════════════════════════════════════════════════════
    
    if commande.statut == 'payee':
        elements.append(Paragraph('<b>INFORMATIONS DE PAIEMENT</b>', header_style))
        
        try:
            paiement = commande.paiement
            paiement_data = [
                ['Mode de paiement:', 'Espèces'],
                ['Date de paiement:', paiement.date_paiement.strftime('%d/%m/%Y à %H:%M')],
                ['Montant payé:', f'{float(paiement.montant):,.0f} GNF'],
            ]
            
            paiement_table = Table(paiement_data, colWidths=[120, 300])
            paiement_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(paiement_table)
            elements.append(Spacer(1, 20))
            
            # Badge "PAYÉ"
            elements.append(Paragraph(
                '<para align="center" fontSize="16" textColor="#059669"><b>✅ PAYÉ</b></para>',
                normal_style
            ))
        except:
            pass
    
    elements.append(Spacer(1, 30))
    
    # ═══════════════════════════════════════════════════════════
    # PIED DE PAGE
    # ═══════════════════════════════════════════════════════════
    
    elements.append(Paragraph('─' * 60, normal_style))
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph(
        '<para align="center" fontSize="10" textColor="#6b7280">'
        'Merci de votre visite !<br/>'
        'Restaurant Manager - Système de Gestion<br/>'
        f'Reçu généré le {timezone.now().strftime("%d/%m/%Y à %H:%M")}'
        '</para>',
        normal_style
    ))
    
    # ═══════════════════════════════════════════════════════════
    # CONSTRUCTION DU PDF
    # ═══════════════════════════════════════════════════════════
    
    doc.build(elements)
    
    # Retourner au début du buffer
    buffer.seek(0)
    return buffer