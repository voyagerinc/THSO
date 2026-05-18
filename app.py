import streamlit as st
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
import io
import json
import os
from datetime import datetime

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(page_title="Excel Template Exporter", layout="wide")

# ============================================================================
# AUTHENTICATION
# ============================================================================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "PaSSw0rd@1"

def check_login():
    """Check if user is logged in"""
    return st.session_state.get('logged_in', False)

def login_page():
    """Display login form"""
    st.title("🔐 Login Required")
    st.markdown("Please login to access the Excel Template Exporter")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", type="primary")
        
        if submit:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state['logged_in'] = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

# Check authentication
if not check_login():
    login_page()
    st.stop()

# ============================================================================
# TEMPLATE MANAGEMENT
# ============================================================================
TEMPLATES_FILE = "templates.json"

def load_templates():
    if os.path.exists(TEMPLATES_FILE):
        try:
            with open(TEMPLATES_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_templates(templates):
    with open(TEMPLATES_FILE, 'w') as f:
        json.dump(templates, f, indent=4)

if 'templates' not in st.session_state:
    st.session_state['templates'] = load_templates()

if 'active_filters' not in st.session_state:
    st.session_state['active_filters'] = []

# ============================================================================
# STYLING CONFIGURATION
# ============================================================================
HEADER_FILL = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
BORDER = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

# ============================================================================
# FILTER & EXPORT LOGIC
# ============================================================================
def get_filtered_dataframe(df_raw, config):
    df_filtered = df_raw.copy()
    
    # 1. Apply filters
    for f in config.get("filters", []):
        if isinstance(f, dict) and "column" in f:
            col = f["column"]
            op = f["operator"]
            val = f["value"]
            
            try:
                num_val = float(val)
                is_num = True
            except ValueError:
                num_val = val
                is_num = False
                
            if col in df_filtered.columns:
                if op == "==":
                    if is_num:
                        df_filtered = df_filtered[df_filtered[col] == num_val]
                    else:
                        search_val = str(val).strip().lower()
                        df_filtered = df_filtered[df_filtered[col].astype(str).str.strip().str.lower() == search_val]
                elif op == "!=":
                    if is_num:
                        df_filtered = df_filtered[df_filtered[col] != num_val]
                    else:
                        search_val = str(val).strip().lower()
                        df_filtered = df_filtered[df_filtered[col].astype(str).str.strip().str.lower() != search_val]
                elif op == ">" and is_num:
                    df_filtered = df_filtered[pd.to_numeric(df_filtered[col], errors='coerce') > num_val]
                elif op == "<" and is_num:
                    df_filtered = df_filtered[pd.to_numeric(df_filtered[col], errors='coerce') < num_val]
                elif op == ">=" and is_num:
                    df_filtered = df_filtered[pd.to_numeric(df_filtered[col], errors='coerce') >= num_val]
                elif op == "<=" and is_num:
                    df_filtered = df_filtered[pd.to_numeric(df_filtered[col], errors='coerce') <= num_val]
                elif op == "contains":
                    df_filtered = df_filtered[df_filtered[col].astype(str).str.contains(str(val), case=False, na=False)]

    # 2. Select columns
    available_cols = [c for c in config.get("columns", []) if c in df_filtered.columns]
    if available_cols:
        df_filtered = df_filtered[available_cols]
    
    # 3. Sort
    sort_cols = [c for c in config.get("sort_by", []) if c in df_filtered.columns]
    if sort_cols:
        df_filtered = df_filtered.sort_values(sort_cols)
        
    return df_filtered

def generate_excel_bytes(df_raw, specific_template_name=None):
    wb = Workbook()
    wb.remove(wb.active)
    
    templates_to_process = st.session_state['templates']
    if specific_template_name and specific_template_name in st.session_state['templates']:
        templates_to_process = {specific_template_name: st.session_state['templates'][specific_template_name]}
    
    if not templates_to_process:
        return None

    for template_name, config in templates_to_process.items():
        df_filtered = get_filtered_dataframe(df_raw, config)
        ws = wb.create_sheet(template_name[:31])
        
        columns = df_filtered.columns.tolist()
        for col_num, col_name in enumerate(columns, 1):
            cell = ws.cell(row=1, column=col_num, value=col_name)
            cell.font = HEADER_FONT
            cell.fill = HEADER_FILL
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = BORDER
        
        for r_idx, row in enumerate(dataframe_to_rows(df_filtered, index=False, header=False), 2):
            for c_idx, value in enumerate(row, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=value)
                cell.border = BORDER
                cell.alignment = Alignment(horizontal="left", vertical="center")
                
                if isinstance(value, (int, float)) and not pd.isna(value):
                    if '.' in str(value):
                        cell.number_format = '0.00'
                    else:
                        cell.number_format = '0'
        
        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            ws.column_dimensions[col_letter].width = min(max_length + 2, 30)
            
        metadata_row = len(df_filtered) + 3
        ws[f'A{metadata_row}'] = f"Filter: {config.get('description', '')}"
        ws[f'A{metadata_row}'].font = Font(italic=True, color="666666", size=9)
        ws[f'A{metadata_row+1}'] = f"Records: {len(df_filtered)}"
        ws[f'A{metadata_row+1}'].font = Font(italic=True, color="666666", size=9)
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

# ============================================================================
# UI LAYOUT
# ============================================================================

st.title("📊 Multi-Template Excel Exporter")
st.markdown("Upload your raw Excel file, design custom templates with filters, and export perfectly formatted multi-sheet Excel files.")

# Logout button
col_logout1, col_logout2 = st.columns([6, 1])
with col_logout2:
    if st.button("🚪 Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

# 1. File Upload
uploaded_file = st.file_uploader("Upload Raw Excel File", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df_raw = pd.read_excel(uploaded_file)
        st.success(f"Successfully loaded {len(df_raw)} rows and {len(df_raw.columns)} columns.")
        
        with st.expander("Raw Data Preview", expanded=False):
            st.dataframe(df_raw.head(100), use_container_width=True)
            
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()
        
    st.divider()
    
    # Split layout into Designer and Saved Templates
    col1, col2 = st.columns([1, 1])
    
    # --- DESIGNER (Left Column) ---
    with col1:
        st.subheader("🛠️ Template Designer")
        
        t_name = st.text_input("Template Name")
        t_cols = st.multiselect("Select Columns to Include", options=df_raw.columns, default=list(df_raw.columns))
        t_sort = st.selectbox("Sort By (Optional)", options=["None"] + list(df_raw.columns))
        
        st.markdown("**Add Filters**")
        f_col1, f_col2, f_col3 = st.columns([2, 1, 2])
        filter_col = f_col1.selectbox("Column", options=df_raw.columns, key="f_col")
        filter_op = f_col2.selectbox("Operator", options=["==", "!=", ">", "<", ">=", "<=", "contains"], key="f_op")
        filter_val = f_col3.text_input("Value", key="f_val")
        
        if st.button("➕ Add Filter"):
            if filter_val != "":
                st.session_state['active_filters'].append({"column": filter_col, "operator": filter_op, "value": filter_val})
                st.rerun()
            else:
                st.warning("Please enter a value for the filter.")
                
        if st.session_state['active_filters']:
            st.markdown("Active Filters:")
            for i, f in enumerate(st.session_state['active_filters']):
                st.write(f"- `{f['column']} {f['operator']} '{f['value']}'`")
            if st.button("Clear Filters"):
                st.session_state['active_filters'] = []
                st.rerun()
                
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Save Template", type="primary"):
            if not t_name:
                st.error("Template Name is required!")
            elif not t_cols:
                st.error("At least one column must be selected!")
            else:
                config = {
                    "description": f"Custom template: {t_name}",
                    "columns": t_cols,
                    "filters": st.session_state['active_filters'].copy(),
                    "sort_by": [t_sort] if t_sort != "None" else []
                }
                st.session_state['templates'][t_name] = config
                save_templates(st.session_state['templates'])
                
                # Clear form state essentially
                st.session_state['active_filters'] = []
                st.success(f"Template '{t_name}' saved successfully!")
                st.rerun()

    # --- SAVED TEMPLATES (Right Column) ---
    with col2:
        st.subheader("📁 Saved Templates")
        
        if not st.session_state['templates']:
            st.info("No templates saved yet. Create one on the left!")
        else:
            selected_t = st.selectbox("Select a Template to Preview", options=list(st.session_state['templates'].keys()))
            
            if selected_t:
                config = st.session_state['templates'][selected_t]
                filtered_df = get_filtered_dataframe(df_raw, config)
                
                st.write(f"**Rows Matched:** {len(filtered_df)}")
                
                if len(filtered_df) == 0 and config.get("filters"):
                    st.warning("Your filter matched 0 rows. Here is some sample data from the columns you filtered to help debug:")
                    for f in config.get("filters", []):
                        c = f.get("column")
                        if c in df_raw.columns:
                            uniq = df_raw[c].dropna().unique()
                            st.write(f"- `{c}`: {', '.join([str(x) for x in uniq[:10]])}")
                
                st.dataframe(filtered_df.head(50), use_container_width=True)
                
                if st.button("🗑️ Delete Template"):
                    del st.session_state['templates'][selected_t]
                    save_templates(st.session_state['templates'])
                    st.rerun()
                
                st.divider()
                st.subheader("📤 Export")
                
                # EXPORT SINGLE
                if len(filtered_df) > 0:
                    excel_data_single = generate_excel_bytes(df_raw, specific_template_name=selected_t)
                    st.download_button(
                        label=f"⬇️ Export SELECTED ({selected_t})",
                        data=excel_data_single,
                        file_name=f"{selected_t}_export.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                # EXPORT ALL
                st.markdown("<br>", unsafe_allow_html=True)
                excel_data_all = generate_excel_bytes(df_raw)
                st.download_button(
                    label="⬇️ Export ALL Templates (Multi-sheet)",
                    data=excel_data_all,
                    file_name="All_Templates_Export.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
