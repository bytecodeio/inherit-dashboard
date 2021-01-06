########################################################
# Import Packages
########################################################
import json
import looker_sdk
import logging
import urllib3
import requests
from looker_sdk import models


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers':'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        }
    }


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))
    body = json.loads(event.get('body'))
    if body is not None:
        base = body.get('baseId')
        customer = body.get('customerId')
        final = body.get('targetId')

        if base is None or customer is None:
            return respond(ValueError('Unspecified arguments for either base dashboard id or customer dashboard id, need both of those'))
        else:
            return respond(err=None, res=MergeDashboards(base=base, customer=customer, final=final))
    else:
        return respond(ValueError('Unspecified arguments, need arguments for (given): base dashboard id, customer dashboard id, and final dashboard id (if null will create)'))


def MergeDashboards(base, customer, final):
    # disable warnings coming from self-signed SSL cert
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    sdk = looker_sdk.init31(config_file='saleseng.ini')

    ####
    # Persist filter overflow and folder types
    #
    ####

    ############## Grab information about dashboard you'd like to copy  ##############
    # NewTitle = input("Enter title for new dashboard: ")
    # BaseDashboard = input("ID of dashboard to copy: ")
    BaseDashboard = base  # Enter the dashboard id of the dashboard you'd like to copy
    # Enter the dashboard id of the customer specific dashboard
    CustomerDashboard = customer
    FinalDashboard = final  # Enter the dashboard id of the combined dashboard
    ################ Step 1 - Get all information about the dashboard to copy ################

    def GetDashboard(dashboard_id=None):
        DashboardToCopy = sdk.dashboard(dashboard_id=str(dashboard_id))
        return DashboardToCopy

    BaseDashboard = GetDashboard(BaseDashboard)
    CustomerDashboardBase = GetDashboard(CustomerDashboard)
    FinalDashboardBase = GetDashboard(FinalDashboard)
    OriginalOutputLayouts = FinalDashboardBase.dashboard_layouts

    # Preserve original dashboard layout, if any, on final dashboard
    FinalDashboardLayout = {}
    for i in OriginalOutputLayouts[0].dashboard_layout_components:
        FinalDashboardLayout[i.element_title] = {
            'width': i.width, 'height': i.height, 'row': i.row, 'column': i.column}

    # print(FinalDashboardLayout)

    # Delete All Elements on Final Dashboard
    FinalDashboardElements = sdk.dashboard_dashboard_elements(
        FinalDashboardBase.id)
    for i in FinalDashboardElements:
        # if i.title == None:
        #     # print(i.title_text)
        # else:
        #     # print(i.title)
        sdk.delete_dashboard_element(i.id)

    # # ############################################################################################

    ##### Step 3 - Get all filters from base dashboard and add to newly created dashboard #######
    # Grab filters from base dashboard
    BaseFilters = sdk.dashboard_dashboard_filters(
        dashboard_id=str(BaseDashboard.id))
    CustomerFilters = sdk.dashboard_dashboard_filters(
        dashboard_id=str(CustomerDashboardBase.id))
    FinalFilters = sdk.dashboard_dashboard_filters(
        dashboard_id=str(FinalDashboardBase.id))

    # # # ###### Step 4 - Get all elements from base dashboard and add to newly created dashboard #######
    BaseDashboardElementsToCopy = sdk.dashboard_dashboard_elements(
        dashboard_id=str(BaseDashboard.id))
    CustomerDashboardElementsToCopy = sdk.dashboard_dashboard_elements(
        dashboard_id=str(CustomerDashboardBase.id))

    # # Add each element from base dashboard to new copied dashboard
    DashboardLayoutsToCopy = sdk.dashboard_dashboard_layouts(BaseDashboard.id)
    CustomerLayoutsToCopy = sdk.dashboard_dashboard_layouts(
        CustomerDashboardBase.id)

    base_names = []
    cust_names = []
    # print('Printing names base')
    for i in DashboardLayoutsToCopy[0].dashboard_layout_components:
        # print(i.element_title)
        base_names.append(i.element_title)

    # print('Printing customer base')
    for i in CustomerLayoutsToCopy[0].dashboard_layout_components:
        # print(i.element_title)
        cust_names.append(i.element_title)

    # print('Printing output base')
    # for i in OutputLayoutsToCopy[0].dashboard_layout_components:
    #     print(i.element_title)
    #     output_names.append(i.element_title)

    # print(base_names)
    # print(cust_names)
    overwrite = list(set(base_names) & set(cust_names))
    # print(overwrite)

    for f in BaseDashboardElementsToCopy:
        if f.title in str(overwrite):
            continue
        else:
            DashboardElementObject = looker_sdk.models.WriteDashboardElement(
                body_text=f.body_text,
                dashboard_id=FinalDashboardBase.id,
                look_id=f.look_id,
                merge_result_id=f.merge_result_id,
                note_display=f.note_display,
                note_state=f.note_state,
                note_text=f.note_text,
                query_id=f.query_id,
                refresh_interval=f.refresh_interval,
                result_maker=f.result_maker,
                result_maker_id=f.result_maker_id,
                subtitle_text=f.subtitle_text,
                title=f.title,
                title_hidden=f.title_hidden,
                title_text=f.title_text,
                type=f.type
            )
            CreatedDashboardElement = sdk.create_dashboard_element(
                body=DashboardElementObject)

    for f in CustomerDashboardElementsToCopy:
        if f.type == 'text':
            continue
        else:
            DashboardElementObject = looker_sdk.models.WriteDashboardElement(
                body_text=f.body_text,
                dashboard_id=FinalDashboardBase.id,
                look_id=f.look_id,
                merge_result_id=f.merge_result_id,
                note_display=f.note_display,
                note_state=f.note_state,
                note_text=f.note_text,
                query_id=f.query_id,
                refresh_interval=f.refresh_interval,
                result_maker=f.result_maker,
                result_maker_id=f.result_maker_id,
                subtitle_text=f.subtitle_text,
                title=f.title,
                title_hidden=f.title_hidden,
                title_text=f.title_text,
                type=f.type
            )
            CreatedDashboardElement = sdk.create_dashboard_element(
                body=DashboardElementObject)

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

    NewDashboardLayouts = sdk.dashboard_dashboard_layouts(
        FinalDashboardBase.id)

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
        dashboard_layout_id=None,
        dashboard_element_id=None,
        row=None,
        column=None,
        width=None,
        height=None,
        deleted=False,
    ):
        LayoutComponentObject = looker_sdk.models.WriteDashboardLayoutComponent(
            dashboard_layout_id=dashboard_layout_id,
            dashboard_element_id=dashboard_element_id,
            row=row,
            column=column,
            width=width,
            height=height,
        )
        UpdatedDashboardLayoutComponent = sdk.update_dashboard_layout_component(
            dashboard_layout_component_id=str(dashboard_layout_component_id), body=LayoutComponentObject)
        return UpdatedDashboardLayoutComponent

    if not FinalDashboardLayout:
        for i in NewDashboardLayouts[0].dashboard_layout_components:
            for j in DashboardLayoutsToCopy[0].dashboard_layout_components:
                if i.element_title == j.element_title:
                    UpdateDashboardLayoutComponent(
                        dashboard_layout_component_id=i.id,
                        dashboard_layout_id=i.dashboard_layout_id,
                        dashboard_element_id=i.dashboard_element_id,
                        # Replace current location with row a
                        row=j.row,
                        column=j.column,
                        width=j.width,
                        height=j.height
                    )

        for i in NewDashboardLayouts[0].dashboard_layout_components:
            for j in CustomerLayoutsToCopy[0].dashboard_layout_components:
                if i.element_title == j.element_title:
                    if j.element_title in str(overwrite):
                        continue
                    else:
                        # print(i.element_title, ' current row: ', i.row)
                        # print(j.element_title, ' needs to be row: ', j.row+row_offset)
                        UpdateDashboardLayoutComponent(
                            dashboard_layout_component_id=i.id,
                            dashboard_layout_id=i.dashboard_layout_id,
                            dashboard_element_id=i.dashboard_element_id,
                            # Replace current location with row a
                            row=j.row + row_offset,
                            column=j.column,
                            width=j.width,
                            height=j.height
                        )
    else:
        # Use original dashboard layouts and tack anything else on at the end
        for i in NewDashboardLayouts[0].dashboard_layout_components:
            for j in DashboardLayoutsToCopy[0].dashboard_layout_components:
                if i.element_title == j.element_title and FinalDashboardLayout.get(i.element_title):
                    # print(FinalDashboardLayout[i.element_title])
                    new_height = FinalDashboardLayout.get(i.element_title, {}).get('height', 0)
                    new_width = FinalDashboardLayout.get(i.element_title, {}).get('width', 0)
                    new_row = FinalDashboardLayout.get(i.element_title, {}).get('row', 0)
                    new_column = FinalDashboardLayout.get(i.element_title, {}).get('column', 0)
                    UpdateDashboardLayoutComponent(
                        dashboard_layout_component_id=i.id,
                        dashboard_layout_id=i.dashboard_layout_id,
                        dashboard_element_id=i.dashboard_element_id,
                        # Replace current location with row a
                        row=new_row,
                        column=new_column,
                        width=new_width,
                        height=new_height
                    )

        for i in NewDashboardLayouts[0].dashboard_layout_components:
            for j in CustomerLayoutsToCopy[0].dashboard_layout_components:
                if i.element_title == j.element_title:
                    if j.element_title in str(overwrite):
                        if j.vis_type == 'text':
                            continue
                        else:
                            continue
                    else:
                        # print(i.element_title, ' current row: ', i.row)
                        # print(j.element_title, ' needs to be row: ', j.row+row_offset)
                        # print(FinalDashboardLayout[i.element_title])
                        new_height = FinalDashboardLayout.get(i.element_title, {}).get('height', 0)
                        new_width = FinalDashboardLayout.get(i.element_title, {}).get('width', 0)
                        new_row = FinalDashboardLayout.get(i.element_title, {}).get('row', 0)
                        new_column = FinalDashboardLayout.get(i.element_title, {}).get('column', 0)
                        if new_row is None:
                            new_row = 0
                        UpdateDashboardLayoutComponent(
                            dashboard_layout_component_id=i.id,
                            dashboard_layout_id=i.dashboard_layout_id,
                            dashboard_element_id=i.dashboard_element_id,
                            # Replace current location with row a
                            row=new_row,
                            column=new_column,
                            width=new_width,
                            height=new_height
                        )

    # Add base filters to new dashboard
    for f in BaseFilters:
        CustomerFilterOverride = None
        FinalFilterOverride = None
        for c in CustomerFilters:
            if c.name == f.name:
                CustomerFilterOverride = c
        
        if CustomerFilterOverride is None:
            for ff in FinalFilters:
                if ff.name == f.name:
                    FinalFilterOverride = ff
            if FinalFilterOverride is None:
                # print('Filter Name: ' + f.name + ', Row: ' + str(f.row)) # Print out filter names and filter row location if you'd like
                DashboardFilterObject = looker_sdk.models.WriteCreateDashboardFilter(
                    dashboard_id=FinalDashboardBase.id,
                    name=f.name,
                    title=f.title,
                    type=f.type,
                    default_value=f.default_value,
                    explore=f.explore,
                    dimension=f.dimension,
                    allow_multiple_values=f.allow_multiple_values,
                    required=f.required,
                    ui_config=f.ui_config,
                    row=f.row,
                    model=f.model,
                    listens_to_filters=f.listens_to_filters,

                )
                sdk.create_dashboard_filter(
                    body=DashboardFilterObject)
            else:
                DashboardFilterObject = looker_sdk.models.DashboardFilter(
                    id=FinalFilterOverride.id,
                    dashboard_id=FinalDashboardBase.id,
                    name=f.name,
                    title=f.title,
                    type=f.type,
                    default_value=f.default_value,
                    explore=f.explore,
                    dimension=f.dimension,
                    allow_multiple_values=f.allow_multiple_values,
                    required=f.required,
                    ui_config=f.ui_config,
                    row=FinalFilterOverride.row,
                    model=f.model,
                    listens_to_filters=f.listens_to_filters,
                    field=f.field,
                )
                sdk.update_dashboard_filter(
                    dashboard_filter_id=FinalFilterOverride.id, body=DashboardFilterObject)

    # Add customer filters to new dashboard
    for f in CustomerFilters:
        FinalFilterOverride = None
        for ffo in FinalFilters:
            if ffo.name == f.name:
                FinalFilterOverride = ffo
        if FinalFilterOverride is None:
            # print('Filter Name: ' + f.name + ', Row: ' + str(f.row)) # Print out filter names and filter row location if you'd like
            DashboardFilterObject = looker_sdk.models.WriteCreateDashboardFilter(
                dashboard_id=FinalDashboardBase.id,
                name=f.name,
                title=f.title,
                type=f.type,
                default_value=f.default_value,
                explore=f.explore,
                dimension=f.dimension,
                allow_multiple_values=f.allow_multiple_values,
                required=f.required,
                ui_config=f.ui_config,
                row=f.row,
                model=f.model,
                listens_to_filters=f.listens_to_filters
            )
            sdk.create_dashboard_filter(body=DashboardFilterObject)
        else:
            DashboardFilterObject = looker_sdk.models.DashboardFilter(
                id=FinalFilterOverride.id,
                dashboard_id=FinalDashboardBase.id,
                name=f.name,
                title=f.title,
                type=f.type,
                default_value=f.default_value,
                explore=f.explore,
                dimension=f.dimension,
                allow_multiple_values=f.allow_multiple_values,
                required=f.required,
                ui_config=f.ui_config,
                row=FinalFilterOverride.row,
                model=f.model,
                listens_to_filters=f.listens_to_filters
            )
            sdk.update_dashboard_filter(
                dashboard_filter_id=FinalFilterOverride.id, body=DashboardFilterObject)

    ##############################################################################################
    
    return 'Success'
    # NewDashboardLayouts = sdk.dashboard_dashboard_layouts(FinalDashboardBase.id)
    # print(len(NewDashboardLayouts))
    # ############################################################################################
