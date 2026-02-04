@memorials_bp.route('/memorials/<int:memorial_id>/pdf', methods=['GET'])
@jwt_required()
def generate_memorial_pdf(memorial_id):
    """Generate a PDF for a memorial"""
    current_user_id = get_jwt_identity()
    
    memorial = Memorial.query.filter_by(id=memorial_id, user_id=current_user_id).first()
    
    if not memorial:
        return jsonify({'error': 'Memorial not found'}), 404
    
    # Prepare data for PDF generation
    memorial_data = {
        'title': memorial.title,
        'name': memorial.name,
        'birth_date': memorial.birth_date.isoformat() if memorial.birth_date else None,
        'death_date': memorial.death_date.isoformat() if memorial.death_date else None,
        'biography': memorial.biography
    }
    
    # Generate PDF
    pdf_content = PDFGenerator.generate_memorial_pdf(memorial_data)
    
    # Create BytesIO object from PDF content
    pdf_file = BytesIO(pdf_content)
    pdf_file.seek(0)
    
    # Send the PDF as a file download
    response = send_file(
        pdf_file,
        as_attachment=True,
        download_name=f'memorial_{memorial_id}_{memorial.name.replace(" ", "_")}.pdf',
        mimetype='application/pdf'
    )
    
    # Add headers to ensure download works
    response.headers['Content-Disposition'] = f'attachment; filename=memorial_{memorial_id}_{memorial.name.replace(" ", "_")}.pdf'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response