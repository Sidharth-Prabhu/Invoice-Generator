import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from PIL import Image as PILImage


class InvoiceGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Invoice Generator")
        self.geometry("800x800")
        self.configure(bg="#f0f0f0")

        self.items = []
        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self, text="Invoice Generator", font=(
            "Helvetica", 20, "bold"), bg="#f0f0f0")
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        labels = [
            "Buyer Name", "GST Number", "Invoice Number", "HSN Code",
            "Dispatched Through", "Dispatched On", "Date", "Mode of Payment",
            "Dispatched Vehicle Number", "Eway Bill Number",
            "CGSTIN", "SGSTIN", "Buyer Address", "Buyer Phone Number"
        ]

        self.entries = {}
        for idx, label in enumerate(labels):
            label_widget = tk.Label(
                self, text=label, bg="#f0f0f0", font=("Helvetica", 10))
            label_widget.grid(row=idx + 1, column=0,
                              sticky=tk.W, padx=10, pady=5)

            if label in ["Buyer Address", "Description of Goods"]:
                self.entries[label] = ScrolledText(
                    self, height=4, width=50, wrap=tk.WORD)
                self.entries[label].grid(
                    row=idx + 1, column=1, padx=10, pady=5)
            else:
                self.entries[label] = tk.Entry(self, width=50)
                self.entries[label].grid(
                    row=idx + 1, column=1, padx=10, pady=5)

        # Add button to add more goods
        self.add_button = ttk.Button(
            self, text="Add More Goods", command=self.open_add_goods_window)
        self.add_button.grid(row=len(labels) + 1,
                             column=0, columnspan=2, pady=10)

        # Button to generate invoice
        self.generate_button = ttk.Button(
            self, text="Generate Invoice", command=self.generate_invoice)
        self.generate_button.grid(
            row=len(labels) + 2, column=0, columnspan=2, pady=10)

    def open_add_goods_window(self):
        AddGoodsWindow(self, self.items)

    def generate_invoice(self):
        invoice_data = {label: self.entries[label].get("1.0", tk.END).strip(
        ) if "Address" in label or "Description" in label else self.entries[label].get().strip() for label in self.entries}

        if not self.items:
            messagebox.showwarning(
                "No Items", "Please add at least one item before generating the invoice.")
            return

        file_path = "invoice.pdf"
        generate_invoice_pdf(file_path, invoice_data, self.items)
        messagebox.showinfo(
            "Success", f"Invoice generated successfully: {file_path}")


class AddGoodsWindow(tk.Toplevel):
    def __init__(self, parent, items):
        super().__init__(parent)
        self.title("Add Goods")
        self.geometry("600x400")
        self.configure(bg="#f0f0f0")
        self.items = items
        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self, text="Add Goods", font=(
            "Helvetica", 16, "bold"), bg="#f0f0f0")
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        labels = [
            "Description of Goods", "Rate", "CGST Rate", "SGST Rate",
            "Quantity", "Per"
        ]

        self.entry_vars = {label: tk.StringVar() for label in labels}
        for idx, label in enumerate(labels):
            label_widget = tk.Label(
                self, text=label, bg="#f0f0f0", font=("Helvetica", 10))
            label_widget.grid(row=idx + 1, column=0,
                              sticky=tk.W, padx=10, pady=5)
            entry_widget = tk.Entry(
                self, textvariable=self.entry_vars[label], width=40)
            entry_widget.grid(row=idx + 1, column=1, padx=10, pady=5)

        self.add_button = ttk.Button(
            self, text="Add Item", command=self.add_item)
        self.add_button.grid(row=len(labels) + 1,
                             column=0, columnspan=2, pady=10)

    def add_item(self):
        item_data = {label: self.entry_vars[label].get()
                     for label in self.entry_vars}
        if not all(item_data.values()):
            messagebox.showwarning(
                "Incomplete Data", "Please fill in all fields.")
            return

        # Calculate Amount
        try:
            rate = float(item_data['Rate'].replace('$', '').replace(',', ''))
            quantity = float(item_data['Quantity'].replace(',', ''))
            cgst_rate = float(item_data['CGST Rate'].replace(
                '$', '').replace(',', ''))
            sgst_rate = float(item_data['SGST Rate'].replace(
                '$', '').replace(',', ''))

            amount = (rate * quantity) + (quantity * (cgst_rate + sgst_rate))
            item_data['Amount'] = f"${amount:.2f}"
            self.items.append(item_data)
            self.destroy()
        except ValueError:
            messagebox.showwarning(
                "Invalid Data", "Please enter valid numbers for rates and quantities.")


def generate_invoice_pdf(file_path, invoice_data, items):
    doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=30,
                            leftMargin=30, topMargin=30, bottomMargin=30)
    story = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['BodyText']

    # Add the branding image at the top
    branding_image_path = "banner.jpeg"  # Update with your image path
    branding_image = PILImage.open(branding_image_path)
    aspect_ratio = branding_image.height / branding_image.width

    # Set the width to fit the page width
    page_width = doc.width
    branding_image = Image(branding_image_path,
                           width=page_width, height=page_width * aspect_ratio)
    story.append(branding_image)
    story.append(Spacer(1, 12))

    # Add Buyer's Address as a paragraph
    buyer_address = invoice_data.get(
        'Buyer Address', '').replace('\n', '<br/>')
    buyer_address_paragraph = Paragraph(
        f"<b>Buyer Address:</b><br/>{buyer_address}", normal_style)
    story.append(buyer_address_paragraph)
    story.append(Spacer(1, 12))

    # Create the invoice details table
    invoice_labels = [
        "Buyer Name", "GST Number", "Invoice Number", "HSN Code",
        "Dispatched Through", "Dispatched On", "Date", "Mode of Payment",
        "Dispatched Vehicle Number", "Eway Bill Number",
        "CGSTIN", "SGSTIN", "Buyer Phone Number"
    ]

    invoice_table_data = [[label, invoice_data.get(
        label, '')] for label in invoice_labels]

    # Create invoice details table
    invoice_table = Table(invoice_table_data, colWidths=[2.5*inch, 3.5*inch])
    invoice_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))

    # Add invoice details table to story
    story.append(invoice_table)
    story.append(Spacer(1, 12))

    # Create the items table
    header = ['Description of Goods', 'CGST Rate',
              'SGST Rate', 'Rate', 'Quantity', 'Per', 'Amount']

    # Calculate Amount and Grand Total
    grand_total = 0
    table_data = [header]

    for item in items:
        rate = float(item['Rate'].replace('$', '').replace(',', ''))
        quantity = float(item['Quantity'].replace(',', ''))
        cgst_rate = float(item['CGST Rate'].replace('$', '').replace(',', ''))
        sgst_rate = float(item['SGST Rate'].replace('$', '').replace(',', ''))
        amount = (rate * quantity) + (quantity * (cgst_rate + sgst_rate))
        item['Amount'] = f"${amount:.2f}"
        grand_total += amount
        table_data.append([item.get(col, '') for col in header])

    items_table = Table(table_data, colWidths=[
        2.5*inch, 0.75*inch, 0.75*inch, 0.75*inch, 0.75*inch, 0.75*inch, 1.0*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))

    story.append(items_table)
    story.append(Spacer(1, 12))

    # Add grand total outside the items table
    grand_total_paragraph = Paragraph(
        f"<b>Grand Total: ${grand_total:.2f}</b>", normal_style)
    story.append(grand_total_paragraph)

    # Build PDF
    doc.build(story)


if __name__ == "__main__":
    app = InvoiceGeneratorApp()
    app.mainloop()
