########################################################
### Import Packages
########################################################
import looker_sdk
import logging
import urllib3
import requests
from looker_sdk import models

# disable warnings coming from self-signed SSL cert
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sdk = looker_sdk.init31(config_file='saleseng.ini') 

############## Grab information about dashboard you'd like to copy  ##############
# NewTitle = input("Enter title for new dashboard: ")
# BaseDashboard = input("ID of dashboard to copy: ")
BaseDashboard = '1186' # Enter the dashboard id of the dashboard you'd like to copy
CustomerDashboard = '1185' # Enter the dashboard id of the customer specific dashboard
FinalDashboard = '1194' # Enter the dashboard id of the combined dashboard
################ Step 1 - Get all information about the dashboard to copy ################
def GetDashboard(dashboard_id=None):
    DashboardToCopy = sdk.dashboard(dashboard_id=str(dashboard_id))
    return DashboardToCopy
BaseDashboard = GetDashboard(BaseDashboard)
CustomerDashboardBase = GetDashboard(CustomerDashboard)
FinalDashboardBase = GetDashboard(FinalDashboard)

# Delete All Elements on Final Dashboard
FinalDashboardElements = sdk.dashboard_dashboard_elements(FinalDashboardBase.id)
for i in FinalDashboardElements:
    if i.title == None:
        print(i.title_text)
    else:
        print(i.title)
    sdk.delete_dashboard_element(i.id)

# # # ############################################################################################

# ##### Step 3 - Get all filters from base dashboard and add to newly created dashboard #######
# Grab filters from base dashboard
# AllFilters = sdk.dashboard_dashboard_filters(dashboard_id=str(BaseDashboard.id))

# # Add to new dashboard
# for f in AllFilters:
#     # print('Filter Name: ' + f.name + ', Row: ' + str(f.row)) # Print out filter names and filter row location if you'd like
#     DashboardFilterObject = looker_sdk.models.WriteCreateDashboardFilter(
#                                                     dashboard_id=FinalDashboardBase.id,
#                                                     name=f.name,
#                                                     title=f.title,
#                                                     type=f.type,
#                                                     default_value=f.default_value,
#                                                     model=f.model,
#                                                     explore=f.explore,
#                                                     dimension=f.dimension,
#                                                     row=f.row,
#                                                     listens_to_filters=f.listens_to_filters,
#                                                     allow_multiple_values=f.allow_multiple_values,
#                                                     required=f.required
#                                                     )
#     NewFilter = sdk.create_dashboard_filter(body=DashboardFilterObject)
# ##############################################################################################

# # # ###### Step 4 - Get all elements from base dashboard and add to newly created dashboard #######
BaseDashboardElementsToCopy = sdk.dashboard_dashboard_elements(dashboard_id=str(BaseDashboard.id))
CustomerDashboardElementsToCopy = sdk.dashboard_dashboard_elements(dashboard_id=str(CustomerDashboardBase.id))

# # Add each element from base dashboard to new copied dashboard
DashboardLayoutsToCopy = sdk.dashboard_dashboard_layouts(BaseDashboard.id)
CustomerLayoutsToCopy = sdk.dashboard_dashboard_layouts(CustomerDashboardBase.id)

base_names = []
cust_names = []
print('Printing names base')
for i in DashboardLayoutsToCopy[0].dashboard_layout_components:
    print(i.element_title)
    base_names.append(i.element_title)

print('Printing customer base')
for i in CustomerLayoutsToCopy[0].dashboard_layout_components:
    print(i.element_title)
    cust_names.append(i.element_title)

print(base_names)
print(cust_names)
overwrite = list(set(base_names) & set(cust_names))
print(overwrite)

for f in BaseDashboardElementsToCopy:
    if f.title in str(overwrite):
        continue
    else:
        DashboardElementObject = looker_sdk.models.WriteDashboardElement(
            body_text= f.body_text,
            dashboard_id= FinalDashboardBase.id,
            look_id= f.look_id,
            merge_result_id= f.merge_result_id,
            note_display= f.note_display,
            note_state= f.note_state,
            note_text= f.note_text,
            query_id= f.query_id,
            refresh_interval= f.refresh_interval,
            result_maker= f.result_maker,
            result_maker_id= f.result_maker_id,
            subtitle_text= f.subtitle_text,
            title= f.title,
            title_hidden= f.title_hidden,
            title_text= f.title_text,
            type= f.type
        )
        CreatedDashboardElement = sdk.create_dashboard_element(body = DashboardElementObject)

for f in CustomerDashboardElementsToCopy:
    DashboardElementObject = looker_sdk.models.WriteDashboardElement(
        body_text= f.body_text,
        dashboard_id= FinalDashboardBase.id,
        look_id= f.look_id,
        merge_result_id= f.merge_result_id,
        note_display= f.note_display,
        note_state= f.note_state,
        note_text= f.note_text,
        query_id= f.query_id,
        refresh_interval= f.refresh_interval,
        result_maker= f.result_maker,
        result_maker_id= f.result_maker_id,
        subtitle_text= f.subtitle_text,
        title= f.title,
        title_hidden= f.title_hidden,
        title_text= f.title_text,
        type= f.type
    )
    CreatedDashboardElement = sdk.create_dashboard_element(body = DashboardElementObject)

# # # # # ############################################################################################

# # # # # ########################## Step 5 - Create all dashboard elements ##########################
# # # # DashboardLayoutsToCopy = sdk.dashboard_dashboard_layouts(dashboard_id=str(BaseDashboard.id))
# # # # for f in DashboardLayoutsToCopy:
# # # #     DashboardElementObject = looker_sdk.models.WriteDashboardLayout(
# # # #         dashboard_id= FinalDashboardBase.id,
# # # #         type= f.type,
# # # #         active= f.active,
# # # #         column_width= f.column_width,
# # # #         width= f.width
# # # #     )
# # # #     CreatedDashboardLayout = sdk.create_dashboard_layout(body = DashboardElementObject)

# # # # # ############################################################################################

# # # # # ############################### Step 6 - Update Layouts ####################################

# # # # # # Get layouts and elements of new dashboard

NewDashboardLayouts = sdk.dashboard_dashboard_layouts(FinalDashboardBase.id) 

rowList = []
heightList = []
for k in DashboardLayoutsToCopy[0].dashboard_layout_components:
    rowList.append(k.row)
    heightList.append(k.height)

max_pos = rowList.index(max(rowList))
max_row_height = heightList[max_pos]
row_offset = max(rowList) + max_row_height
print(row_offset)

def UpdateDashboardLayoutComponent(
                            dashboard_layout_component_id=None,
                            dashboard_layout_id= None,
                            dashboard_element_id= None,
                            row= None,
                            column= None,
                            width= None,
                            height= None
                            ):
    LayoutComponentObject = looker_sdk.models.WriteDashboardLayoutComponent(
                        dashboard_layout_id= dashboard_layout_id,
                        dashboard_element_id= dashboard_element_id,
                        row= row,
                        column= column,
                        width= width,
                        height= height
                        )
    UpdatedDashboardLayoutComponent = sdk.update_dashboard_layout_component(dashboard_layout_component_id=str(dashboard_layout_component_id), body = LayoutComponentObject)
    return UpdatedDashboardLayoutComponent

for i in NewDashboardLayouts[0].dashboard_layout_components:
    for j in DashboardLayoutsToCopy[0].dashboard_layout_components:
        if i.element_title == j.element_title:
            UpdateDashboardLayoutComponent(
                dashboard_layout_component_id= i.id,
                dashboard_layout_id= i.dashboard_layout_id,
                dashboard_element_id= i.dashboard_element_id,
                # Replace current location with row a
                row= j.row,
                column= j.column,
                width= j.width,
                height= j.height
                )

for i in NewDashboardLayouts[0].dashboard_layout_components:
    for j in CustomerLayoutsToCopy[0].dashboard_layout_components:
        if i.element_title == j.element_title:
            if j.element_title in str(overwrite):
                continue
            else:
                print(i.element_title, ' current row: ', i.row)
                print(j.element_title, ' needs to be row: ', j.row+row_offset)
                UpdateDashboardLayoutComponent(
                    dashboard_layout_component_id= i.id,
                    dashboard_layout_id= i.dashboard_layout_id,
                    dashboard_element_id= i.dashboard_element_id,
                    # Replace current location with row a
                    row= j.row + row_offset,
                    column= j.column,
                    width= j.width,
                    height= j.height
                    )

NewDashboardLayouts = sdk.dashboard_dashboard_layouts(FinalDashboardBase.id) 
print(len(NewDashboardLayouts))
# ############################################################################################
