import io
import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

MAPPING = {
    "a": 0,
    "b": 1,
    "c": 0,
    "d": 1,
    "e": 0,
    "f": 3,
    "g": 2,
    "h": 1,
    "i": 0,
    "j": 2,
    "k": 1,
    "l": 1,
    "m": 0,
    "n": 0,
    "o": 0,
    "p": 2,
    "q": 2,
    "r": 0,
    "s": 0,
    "t": 1,
    "u": 0,
    "v": 0,
    "w": 0,
    "x": 0,
    "y": 2,
    "z": 0
}

def get_shape(value):
    shapes = [(0, 1, 0), (0, 1, 1), (1, 1, 0), (1, 1, 1)]
    return shapes[MAPPING[value]]

def get_word_shapes(word):
    return [get_shape(letter) for letter in word]


def draw_table(margin_x, number_width,
               page_height, margin_y, table_number,
               table_height, gap_y, pdf,
               cell_width, row_heights, columns_to_draw):

    # Position of table
    x0 = margin_x + number_width
    y0 = (
        page_height
        - margin_y
        - (table_number + 1) * table_height
        - table_number * gap_y
    )

    # Vertically center the number
    number_y = y0 + table_height / 2 - 3
    pdf.drawString(margin_x, number_y, str(table_number + 1))

    # -------------------------------------------------
    # Draw the vertical lines of each active square
    # -------------------------------------------------
    for col, pattern in enumerate(columns_to_draw):

        for row, draw in enumerate(pattern):

            if not draw:
                continue

            x = x0 + col * cell_width
            y = y0 + sum(row_heights[:row])
            cell_height = row_heights[row]

            # Left edge
            pdf.line(
                x, y,
                x, y + cell_height
            )

            # Right edge
            pdf.line(
                x + cell_width, y,
                x + cell_width, y + cell_height
            )

            # -------------------------------------------------
            # Bottom edge
            # Only draw if there isn't an active square below
            # -------------------------------------------------
            if row == 0 or not pattern[row - 1]:
                pdf.line(
                    x, y,
                    x + cell_width, y
                )

            # -------------------------------------------------
            # Top edge
            # Only draw if there isn't an active square above
            # -------------------------------------------------
            if row == len(pattern) - 1 or not pattern[row + 1]:
                pdf.line(
                    x, y + cell_height,
                    x + cell_width, y + cell_height
                )




def create_pdf(words, y_gap_mm=3):
    word_shapes = [get_word_shapes(word) for word in words]

    buffer = io.BytesIO()

    # A4 portrait
    page_width, page_height = A4

    pdf = canvas.Canvas(buffer, pagesize=A4)

    # Page margins
    margin_x = 10 * mm
    margin_y = 5 * mm

    # -------------------------------------------------
    # Layout: 10 tables in ONE column
    # -------------------------------------------------
    table_count = 10

    # Space between tables
    gap_y = y_gap_mm * mm

    # Space reserved for table number
    number_width = 8 * mm

    # Available page area
    available_width = (
        page_width
        - (2 * margin_x)
        - number_width
    )

    available_height = (
        page_height
        - (2 * margin_y)
    )

    # Height of each table
    table_height = (
        available_height
        - gap_y * (table_count - 1)
    ) / table_count

    table_width = available_width

    # -------------------------------------------------
    # Each table = 20 columns × 3 rows
    # -------------------------------------------------
    cols = 20

    cell_width = table_width / cols

    # Heights of bottom, middle, top rows
    top_height = table_height * 0.20
    middle_height = table_height * 0.50
    bottom_height = table_height * 0.20

    row_heights = [
        bottom_height,
        middle_height,
        top_height,
    ]


    # Thin grid lines
    pdf.setLineWidth(0.25)

    # Number font
    pdf.setFont("Helvetica-Bold", 8)

    # Draw tables
    for table_number, columns_to_draw in enumerate(word_shapes):

        draw_table(margin_x, number_width, 
                page_height, margin_y, table_number, 
                table_height, gap_y, pdf, 
                cell_width, row_heights, columns_to_draw)

    # One page only
    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    return buffer.getvalue()


def is_alphabet_chars_only(s):
    parts = [part.lower().strip() for part in s.split(",")]
    if all(part and all("a" <= c <= "z" for c in part) for part in parts):
        return parts


# -------------------------
# Streamlit UI
# -------------------------

st.title("Word Shape Generator")

st.markdown(
    "Generate one A4 portrait page containing up to 10 word shapes with up to 20 characters.  \n"
    "e.g. **tiny,large,monkey,flappy,bird**"
)


text_entry = st.text_input("Enter words here:")

if st.button("Generate PDF"):

    if text_entry.strip() == "":
        st.error("You haven't entered any words!")
    else:
        words = is_alphabet_chars_only(text_entry)
        if words is None:
            st.error('Only characters a-z, separated by commas are allowed. No special characters or symbols.')
        else:
            pdf_bytes = create_pdf(words)

            st.success("PDF created successfully.")

            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name="10_numbered_tables_50x3.pdf",
                mime="application/pdf",
            )
