------------------------------------------
Application Monitoring with Prism Ultimate
------------------------------------------

      .. figure:: images/operationstriangle.png

Prism Pro brings smart automation to our customer’s daily IT operations. With Prism Ultimate we expand this smart automation and intelligent learning to the application and services layers. The typical operations workflow is a continuous cycle of monitoring, analyzing and taking action where necessary. Prism Pro mirrors traditional IT Admin's workflows to improve operations efficiency and Prism Ultimate combines that with full-stack visibility. With Prism Ultimate, IT Admins are able to connect insights from application machine data to automate this typical flow using the power of the machine learning engine X-FIT and the X-Play automation engine.

In this lab you will learn how Prism Ultimate can help IT Admins monitor, analyze and automatically act when a SQL Server's performance is impacted. You will also see how you can discover applications running on your cluster with Prism Ultimate.

.. _sqlservermonitoring:

SQL Server Monitoring with Prism Ultimate
+++++++++++++++++++++++++++++++++++++++++

Prism Ultimate licensing includes the SQL Server monitoring pack, which allows IT admins to understand how infrastructure may impact applications and vice versa. This is an agentless solution that gives visibility into databases, queries, SQL metrics and applies the X-FIT behavior learning and anomaly detection capabilities.

#. Within Prism Central, click on :fa:`bars` **Operations > Integrations**.

      .. figure:: images/appmonitoring0.png

#. Click **Get Started** to configure the monitoring integration. The *Monitoring Integrations* screen will appear. This is the page where the your configured integrations would show up.

#. Click on **Configure Instance**.

      .. figure:: images/appmonitoring2.png

#. Select **Microsoft SQL Server** from the dropdown, check the box for *I have increase Prism Central (PC) VM's Memory and vCPU* (please see the note directly below), and then click **Enable**. This allows Nutanix Collector to collect external entity instance metrics. In this case, the SQL Server collector is already enabled, you will not see that option and can skip to the next step.

   .. note::

      Pay close attention to the other features you may have, or will enable in Prism Central in addition to what is outlined in this workshop. Please refer to `Prism Central: Resource Requirements for various services enablement on Prism Central <https://portal.nutanix.com/page/documents/kbs/details?targetId=kA00e000000brBgCAI>`_ for considerations regarding resources.

#. Select the IP address of you MSSQL server VM within the *Microsoft SQL Server Host*. Fill in the rest of the fields with the information listed below. The *Microsoft SQL Server Port* field should be auto-filled with 1433 (standard SQL port). Click on **Test Connection**, and once that is successful, click **Save**.

   - **Microsoft SQL Server Port** 1433
   - **username:** sa
   - **password:** Nutanix/1234

      .. figure:: images/appmonitoring5.png

#. Once complete, your SQL Server will be listed under *Monitoring Integrations*, as seen below.

      .. figure:: images/appmonitoring6.png

#. Click on the IP Address of the server, under the *Name* column to observe the information being collected. The *Summary* screen is now shown.

      .. figure:: images/appmonitoring7.png

#. In addition to the *Summary* view, click **Queries** from the left-hand menu to observe SQL Server queries, sorted by highest average execution time, providing greater insight into the application itself.

      .. figure:: images/sqlqueries.png

#. Click **Metrics** from the left-hand menu. As SQL monitoring has recently been setup, it will take time for these metrics to full populate. In the example below, we can see that in the *CPU Utilization* chart anomalies are generated based on machine learned baselines, just as Prism Pro provides on the VM level.

      .. figure:: images/sqlcharts.png

   Next, we will create an alert policy for the *Buffer Pool Size*, and a playbook based on that alert, to extend the simplicity of our powerful X-Play automation onto applications as well.

#. Scroll down to the **Buffer Pool Size** metric (typically 3rd from the bottom, right column), click on **Actions**, and then choose **Alert Settings**.

      .. figure:: images/bufferalert1.png

   We will be stressing the SQL Server in a later step using an application called *HammerDB*. The stress will cause the metric to increase after a short delay. We will keep the alert threshold at a fair number so to get the alert policy raised as soon as possible for our example.

#. Within the *Static Threshold* section, click the checkbox for **Alert Critical if** and within the field to the right of the *>=* dropdown, enter **100**.

#. From the dropdown for *Trigger alert if conditions persist for*, select **0 Minutes**.

#. Within *Policy Name* enter *Initials*\ **- SQL Server Buffer Pool Size**, and click **Save**.

      .. figure:: images/bufferalert2.png

#. Within Prism Central, click on :fa:`bars` **Operations > Playbooks**.

   Next, we will create the playbook the alert policy will trigger, which includes a PowerShell script to collect and upload logs to a Google Drive.

#. Select the *List* menu on the left-hand, click **Get Started** (if displayed), and then **Create Playbook**.

#. Within the *Select a Trigger* screen, click **Alert**.

#. From the *Select an Alert Policy* dropdown, select *Initials*\ **- MSSQL Buffer Pool Size**.

      .. figure:: images/sqlplay1.png

   The built-in PowerShell script requires our MSSQL VM IP address, which we will obtain by creating *Action* entries. The first one will be to the lookup the VM IP.

#. From the left-hand side, click **Add Action** below the *Actions* section.

#. Click **Select** on the *REST API* action.

   Next, We will utilize Nutanix APIs to collect the VM metrics.

#. Directly to the right of *REST API*, click the :fa:`pencil` and enter **Look up VM IP** in the *Add Description* field, and click **Save**.

#. Within the *Method (Optional)* dropdown, select **POST**, and fill out all fields as indicated.

   .. note::

   While the field names in this example include the phrase *(Optional)*, they are required for this step.

   - **URL:** `https://<PRISM-CENTRAL-IP-ADDRESS>:9440/api/nutanix/v3/groups`
   - **Username (Optional)** admin
   - **Password (Optional)** <PRISM-CENTRAL-ADMIN-PASSWORD>
   - **Request Body (Optional)**

      .. code-block:: bash

         {"entity_type":"ntnxprismops__microsoft_sqlserver__instance","entity_ids": ["{{trigger[0].source_entity_info.uuid}}"],"query_name":"eb:data-1594987537113","grouping_attribute":" ","group_count":3,"group_offset":0,"group_attributes":[],"group_member_count":40,"group_member_offset":0,"group_member_sort_attribute":"active_node_ip","group_member_sort_order":"DESCENDING","group_member_attributes":[{"attribute":"active_node_ip"}]}

   - **Request Headers (Optional)** `Content-Type:application/json`

      .. figure:: images/sqlplay3.png

   We will use the *String Parser* action to extract the VM IP from the preceding action.

#. From the left-hand side, click **Add Action** below the *Actions* section.

#. Click **Select** on the *String Parser* action.

#. Directly to the right of *String Parser*, click the :fa:`pencil`, enter **Extract VM IP** in the *Add Description* field, and click **Save*.

#. Directly below the *String to Parse* field, click **Parameters**, and select **Response Body** within the *Previous Action* column.

#. Enter the below into the *JSON Path* field.

   - **JSON Path**

      .. code-block:: bash

      $.group_results[0].entity_results[0].data[0].values[0].values[0]

      .. figure:: images/sqlplay5.png

#. From the left-hand side, click **Add Action** below the *Actions* section.

#. Click **Select** on the *IP Address Powershell* action.

#. Directly to the right of *IP Address Powershell*, click the :fa:`pencil`, enter **Upload to Google Drive** in the *Add Description* field, and click **Save*.

#. Directly below the *IP Address/Hostname* field, click **Parameters**, and select **Parsed String** within the *Previous Action* column. Fill out the following fields as indicated:

   - **Username** Administrator
   - **Password** Nutanix/4u
   - **JSON Path:** `C:\\Users\\Administrator\\Desktop\\UploadToGDrive.ps1-id <INITIALS>`

#. Slide *HTTPS* to the left (disabled).

      .. figure:: images/sqlplay7.png

#. From the left-hand side, click **Add Action** below the *Actions* section.

#. Click **Select** on the *Email* action.

   The e-mail will serve as notification that an alert has been raised, that a log file has been uploaded to Google Drive (with  link). Fill out the following fields as indicated:

   - **Recipient** Your e-mail address (ex. `first.last@nutanix.com`).
   - **Subject** ``X-Play notification for {{trigger[0].alert_entity_info.name}}``
   - **Message** ``This is a message from Prism Pro X-Play. Logs have been collected for your SQL server due to a high buffer pool size event and are available for you at https://drive.google.com/drive/folders/1e4hhdCydQ5pjEKMXUoxe0f35-uYshnLZ?usp=sharing``

      .. figure:: images/sqlplay9.png

#. Click **Save & Close**.

#. Enter *Initials*\ **- High Buffer Pool Size** in the *Name* field.

#. Slide the *Playbook Status* to the right (Enabled), and click **Save**.

      .. figure:: images/sqlplay10.png

   Now we will trigger the workflow.

#. Within Prism Central, click on :fa:`bars` **Virtual Infrastructure > VMs**.

#. Right-click on your MSSQL VM, and choose **Launch Console**.

#. Log in using the following credentials:

   - **Username** Administrator
   - **Password** Nutanix/4u

   We will now artificially generate the required usage to activate the alert we previously created. To do so, we will be executing a PowerShell script, which utilizes a program called HammerDB.

#. Using *File Explorer*, navigate to **Local Disk(C:) > Program Files > HammerDB**.

#. Right-click on the file *workload.ps1*, and select **Run with Powershell**.

      .. figure:: images/hammerdb.png

#. It may take up to 5 minutes for the activity generated by the PowerShell script to meet the requirements for the alert. During this time, you may review the *Application Discovery* section below.

#. You will notice an alert within *Prism Central*, if you navigate to **Activity > Alerts**, or by clicking the :fa:`bell` icon in the upper right hand corner.

      .. figure:: images/pcalert.png

#. Additionally, you will receive an e-mail advising you of the triggered alert. It may take up to 5-10 minutes to be received.

      .. figure:: images/sqlemail.png

#. Click on the URL in the email, or https://drive.google.com/drive/folders/1e4hhdCydQ5pjEKMXUoxe0f35-uYshnLZ?usp=sharing, to confirm the log file has been uploaded.

#. Within Prism Central, click on :fa:`bars` **Operations > Playbooks**. Select **Plays** from the left-hand menu.

#. Click on the *Initials*\ **- High Buffer Pool Size** Playbook to review the actions that were executed for this playbook. The sections in this view can be expanded to show more details for each item, by clicking the down arrow at the right of each entry.

      .. figure:: images/sqlplay11.png

Importing/Exporting Playbooks
+++++++++++++++++++++++++++++

Import Playbook
...............

#. Download this `Playbook <https://drive.google.com/file/d/1lyVoKI0Xf0lJgC4k9aAfMTdztWD0fVMT/view?usp=sharing>`_.

#. Within Prism Central, click on :fa:`bars` **Operations > Playbooks**.

#. Select **List** from the left-hand menu, then click on **Import**.

#. Click the **Browse** button, and select the Playbook you previously downloaded, then click **Import**.

   You may see *Validation Errors* as the status, as certain information such as credentials and URLs are be different for your environment. We will resolve these errors in the proceeding step.

#. Click on the *<Initials> - SQL Log Collection - Imported (date/time)* Playbook.

   The actions that have validation errors have been highlighted. It is recommended that you review all actions, not just the entries highlighted in red, to confirm that the information in correct.

#. Click **Update**, and enter the correct information from the :ref:`sqlservermonitoring` section.

#. Once all fields have the correct information, click **Save & Close**. If validation errors are still present, you will be notified upon saving.

#. Enter *Initials*\ **- SQL Log Collection** in the *Name* field.

#. Slide the *Playbook Status* to the right (Enabled), and click **Save**.

Export Playbook
...............

#. Within Prism Central, click on :fa:`bars` **Operations > Playbooks**.

#. Select **List** from the left-hand menu, then click on **Import**.

#. Click on the *Initials*\ **- SQL Log Collection** Playbook.

#. Click on the *More* dropdown (upper right), and select **Export**.

#. Enter *Initials*\ **- SQL Log Collection - Export** in the *Name* field.

#. The exported *Initials*\ **- SQL Log Collection - Export.PBK** file will be downloaded by your browser, and available for future use.

Application Discovery with Prism Ultimate
+++++++++++++++++++++++++++++++++++++++++

Prism Ultimate gives the capability to discover applications, identify application to VM dependency, and provide a view of the full stack.

#. Within Prism Central, click on :fa:`bars` **Operations > App Discovery**.

#. Click on **Enable App Discovery** (if available), otherwise click **Discover** to begin the discovery process on your cluster. Once complete, you will be presented with a summary of the apps discovered, and identified.

#. Click on **View App Instances**.

      .. figure:: images/appdiscovery3.png

#. Review the list of apps, and observe that there are some apps listed as *Unknown*. Select any of these apps, then click on **Actions > Identify** to setup a policy to identify the app.

      .. figure:: images/appdiscovery4.png

#. You can identify an app by the port(s), as they will be automatically input into the corresponding field.

#. Give the app an appropriate name (ex. *Initials*\ **- My Special App**, then click on **Save and Apply**.

      .. figure:: images/appdiscovery5.png

#. Observe that the app is no longer listed as *Unknown*, and that the new identification policy you've created has been applied. Any future apps that match the policy you created, will be identified in the same way.

      .. figure:: images/appdiscovery6.png

#. Select the policy, and click **Actions > Delete**. Observe that the app you previously identified (via the policy you created) is once again listed as *Unknown*.

      .. figure:: images/appdiscovery7.png

Takeaways
+++++++++

   - Prism Ultimate bridges the gap between infrastructure, applications, and services. It satisfies IT OPS processes ranging from intelligent detection, to automated remediation.

   - X-Play, the "IFTTT" for the enterprise, is our engine to enable the automation of daily operations tasks, enabling admins of every skill level to build custom automations to aid them in their daily duties.

   - Prism Ultimate allows the admin to understand the relationship between their applications and infrastructure, with broader visibility and intelligent insights learning.

   - X-Play can be used seamlessly with the application data monitored via Prism Ultimate to build smart automation that can alert and remediate issues both on the infrastructure and on applications.
