------------------------------------------
Application Monitoring with Prism Ultimate
------------------------------------------

.. figure:: images/operationstriangle.png

Prism Pro brings smart automation to our customer’s daily IT operations. With Prism Ultimate we expand this smart automation and intelligent learning to the application and services layers. The typical operations workflow is a continuous cycle of monitoring, analyzing and taking action where necessary. Prism Pro mirrors traditional IT Admin's workflows to improve operations efficiency adn Prism Ultimate combines that with full-stack visibility. With Prism Ultimate, IT Admins are able to connect insights from application machine data to automate this typical flow using the power of the machine learning engine X-FIT and the X-Play automation engine.

In this lab you will learn how Prism Ultimate can help IT Admins monitor, analyze and automatically act when a SQL Server's performance is impacted. You will also see how you can discover applications running on your cluster with Prism Ultimate.

Lab Setup
+++++++++

#. Open your **Prism Central** and navigate to the **VMs** page. Note down the IP Address of the **PrismOpsLabUtilityServer**. You will need to access this IP Address throughout this lab.

   .. figure:: images/init1.png

#. Open a new tab in the browser, and navigate to http://`<PrismOpsLabUtilityServer_IP_ADDRESS>`/alerts [example http://10.38.17.12/alerts]. It is possible you may need to log into the VM if you are the first one to use it. Just fill out the **Prism Central IP**, **Username** and **Password** and click **Login**.

   .. figure:: images/init2.png

#. Once you have landed on the alerts page, leave the tab open. It will be used in a later portion of this lab.

   .. figure:: images/init2b.png

#. In a separate tab, navigate to http://`<PrismOpsLabUtilityServer_IP_ADDRESS>`/ to complete the lab from [example http://10.38.17.12/]. Use the UI at this URL to complete the lab.

   .. figure:: images/init3.png


SQL Server Monitoring with Prism Ultimate
+++++++++++++++++++++++++++++++++++++++++++

Prism Ultimate includes the SQL Server monitoring pack which allows IT admin to understand how infrastructure may impact applications and vice versa. This is an agentless solution that gives visibility into databases, queries and SQL metrics and applies the X-FIT behavior learning and anomaly detection capabilities.

Prism Pro now also has the ability to import and export playbooks. The steps to do so for the playbook created below are listed in the next section. You will need to complete the rest of the steps such as setting up the alert policy and stressing the SQL Server but if you understand how playbooks function and can be created easily you can leverage the file provided in the next section and follow the steps to save some time. We recommend reading through the steps to create trhe playbook and understanding them properly. 

#. Go to Integrations from the Prism Central home page

   .. figure:: images/appmonitoring0.png

#. Click **Get Started** to start setting up a monitoring integration. 

   .. figure:: images/appmonitoring1.png

#. This is the page where the your configured integrations would show up. Click on **Configure instances**.

   .. figure:: images/appmonitoring2.png

#. Choose **Microsoft SQL Server** from the dropdown(the other option being vCenter) and click on **Enable** so that the Nutanix collector can start collecting external metrics. 

   .. figure:: images/appmonitoring3.png

#. Choose your SQL VM Host IP from the dropdown list 

   .. figure:: images/appmonitoring4.png

#. Fill in the rest of the fields with the credentials listed below. The port should be auto-filled with 1433, the standard SQL port. Click on **Test Connection** and then hit **Save** once it is successful. 

   - **username: sa** 
   - **password: Nutanix/1234**.

   .. figure:: images/appmonitoring5.png

#. You should see your SQL Server show up under integrations like in the figure below. Click on the Server Name(IP Address) to have a look at what is being collected. 

   .. figure:: images/appmonitoring6.png

#. In addition to the summary view, you can look at the databases running on the SQL Server, SQL Specific metrics impacting the server's performance and queries sorted by highest average execution time to provide a better insight into the application. 

   .. figure:: images/sqlqueries.png

#. Now we will create an alert policy for the **Buffer Pool Size** and a playbook based on that alert so we can see how we can extend the simplicity of our powerful X-Play automation onto applications as well with Prism Ultimate. Scroll down to the **Buffer Pool Size** metric and click on **Actions** and choose **alert settings**.

   .. figure:: images/bufferalert1.png

#. We will be stressing the SQL Server in a later step using an application called **HammerDB**. The stress will cause the metric to go very high after a delay of a few minutes. We will keep the alert threshold at a fair number so to get the alert policy raised as soon as possible for our example. Set the static threshold for the critical alert at **300mib** like show in the figure below. Also make sure to change the policy name to something **Initials - SQL Server Buffer Pool Size**. Click save and go to playbooks under the Operations tab. 

   .. figure:: images/bufferalert2.png

#. Now we will create the playbook which we want to execute when this alert policy is triggered. The actions we want to take are running a powershell script on the VM to collect logs and then uploading those logs onto a google drive so we can review what went wrong. Choose Alert as the trigger for your playbook and specifiy the alert policy you just created. You can also skip to the next section to import the playbook the next steps are for, you **Will** need to complete the rest of the steps to trigger the workflow so read through the instructions carefully. 

   .. figure:: images/sqlplay1.png

#. We have to get the VM IP Address so we can use the out of the box **Powershell** action to run our script. So we will need to create a couple of actions first. The first one will be to the lookup the VM IP. Click on **Add Action** and select the **REST API** action.

   .. figure:: images/sqlplay2.png

#. We use our Nutanix v3 APIs to collect the VM metrics. Select the **POST** method. You will need to enter the Prism Central credentials that were used to login. Fill in the rest of the fields according to below replacing the <PrismCentral_IP_ADDRESS> with your own. 

   - **Method:** POST
   - **URL:** https://<PrismCentral_IP_ADDRESS>/api/nutanix/v3/groups
   - **Request Body:** ``{"entity_type":"ntnxprismops__microsoft_sqlserver__instance","entity_ids": ["{{trigger[0].source_entity_info.uuid}}"],"query_name":"eb:data-1594987537113","grouping_attribute":" ","group_count":3,"group_offset":0,"group_attributes":[],"group_member_count":40,"group_member_offset":0,"group_member_sort_attribute":"active_node_ip","group_member_sort_order":"DESCENDING","group_member_attributes":[{"attribute":"active_node_ip"}]}``
   - **Request Header:** Content-Type:application/json

   .. figure:: images/sqlplay3.png

#. Click add action and select the **String Parse** action so that we can extract the VM IP from the previous action. 

   .. figure:: images/sqlplay4.png

#. Use the **Parameter** link to choose the **Response Body** from the previous action. Add in the following JSON path and fill in the rest of the fields as shown in the figure below. 

   - **JSON Path:** ``$.group_results[0].entity_results[0].data[0].values[0].values[0]``

   .. figure:: images/sqlplay5.png

#. Click **Add Action** to add the next action and select the **IP Address Powershell** action. 

   .. figure:: images/sqlplay6.png

#. Use the **Parameters** link to get the parsed string from the previous action i.e. the VM IP for the **IP Address/Hostname** field. Provide the SQL VM credentials listed below. Provide the followng path to script and repalce <Name> with your name so you can recognize your log file in the google drive. 

   - **Username: Administrator** 
   - **Password: Nutanix/4u**.
   - **JSON Path:** C:\\Users\\Administrator\\Desktop\\UploadToGDrive.ps1 -id <Name>

  .. figure:: images/sqlplay7.png

#. Now we'll add the last action for the playbook, Click **Add Action** and select the **Email** action to send an email. 

  .. figure:: images/sqlplay8.png

#. In the email we want to let teh user know that a alert has been raised and a log file has been uploaded to a google drive link that we will provide so they can take a look. Fill in the following fields

      - **Recipient:** - Fill in your email address.
      - **Subject :** - ``X-PLay notification for {{trigger[0].alert_entity_info.name}}``
      - **Message:** - ``TThis is a message from Prism Pro X-Play. Logs have been collected for your SQL server due to a high buffer pool size event and are available for you at https://drive.google.com/drive/folders/1e4hhdCydQ5pjEKMXUoxe0f35-uYshnLZ?usp=sharing``

  .. figure:: images/sqlplay9.png

#. Click **Save & Close** button and save it with a name “*Initials* - High Buffer Pool Size”. **Be sure to enable the ‘Enabled’ toggle.**

  .. figure:: images/sqlplay10.png

#. Now we will trigger the workflwpw, launch the console for your VM where the SQL Server is running using the credentials listed below. There is a *HammerDB* application already installed on the VM. In order to cause a spike in the metrics we will run a powershell script to create some users on the Server, Go to **Local Disk(C:) > Program Files > HammerDB** and right-click on the file **workload.ps1** and select **Run with Powershell** as shown in the figure below. 

   - **Username: Administrator**
   - **Password: Nutanix/4u**.

 .. figure:: images/hammerdb.png 

#. It may take up to 5 minutes for the metrics to spike on the Server, you can skip to the **Appplication Discovery** section below in the meantime which should take roughly the same amount of time in which the policy is raised and the playbook is executed. 

#. You should recieve an email to the email address you put down in the first playbook. It may take up to 5-10 minutes. 

  .. figure:: images/sqlemail.png

#. Click on the URL in the email to go to the google drive or go directly to https://drive.google.com/drive/folders/1e4hhdCydQ5pjEKMXUoxe0f35-uYshnLZ?usp=sharing and confirm that the log file has been uploaded. 

  .. figure:: images/sqllogfile.png

#. Switch back to the previous tab with the Prism Central console open. Open up the details for the **`Initials` - High Buffer Pool Size** Playbook that you created and click the **Plays** tab towards the top of the view to take a look at the Plays that executed for this playbook. The sections in this view can be expanded to show more details for each item. If there were any errors, they would also be surfaced in this view.

 .. figure:: images/sqlplay11.png


Importing/Exporting Playbooks
+++++++++++++++++++++++++++++++++++++++++++

X-Play now has the ability to import and export playbooks across Prism Centrals. In the example below we will show how to import the playbook that is created in the preceding steps. The user will still need to create the alert policies and go through the workflow to trigger the alert as listed in the steps in the previous section.

#. Go to Playbooks page and click on **Import** 

 .. figure:: images/import0.png

#. You will need to choose the Binary file that you downloaded as the playbook to import. 

 .. figure:: images/import1.png

#. You will see some validation errors since the certain fields such as credentials and URLs will be different for your environment. Click on **Import**, we will resolve these errors in the next step.

 .. figure:: images/import2.png

#. Click on the playbook that has just been imported for you - there will be a time stamp in the playbook name. Once open the you will see that the actions that have validation errors have been highlighted. Even for actions that have not been highlighted make sure to confirm that the information such as **Passwrods**, **URLs** and **IP Addresses** is correct according to your environment. Refer to the playbook creation steps above to confirm these fields

 .. figure:: images/import3.png

#. Once you have changed these fields click on **Save & Close**. If validation errors are still present, the pop-up will say so. otherwise remember to click **Enable** and add your Initials to the playbook name before clicking **Save**

 .. figure:: images/import4.png


Application Discovery with Prism Ultimate
+++++++++++++++++++++++++++++++++++++++++++

Prism Ultimate gives the capability to discover applications running on your ESXi cluster to identify applciation to VM dependency and get a view of the full stack. 

#. Using the hamburger menu navigate to **Operations > App Discovery**

 .. figure:: images/appdiscovery1.png

#. Once on the **App Discovery** page click on **Discover** to start discovering the apps running on your cluster. 

 .. figure:: images/appdiscovery2.png

#. Discovery will run and give you a summary of the apps discovered and identified. Click on **View App Instances** to view the list. You can run **Discover** periodically by coming to this page to identify new apps. 

 .. figure:: images/appdiscovery3.png

#. Going through the list of apps, you will see there is an **Unknown** app in the list. Select the app and click on **Actions** to setup a policy to identify the app. 

 .. figure:: images/appdiscovery4.png

#. You can identify this app by the Ports that will be auto-filled by Discovery. Name this app, example **Initials - My Special App** and click on **Save and Apply**. 

 .. figure:: images/appdiscovery5.png

#. Now you can see the identified app in your list and check that the new identification policy you created has been added to the **Policies** list. Any future apps with these ports will be identified under the same policy. 

 .. figure:: images/appdiscovery6.png

#. Delete your policy so that the other users may setup their own. Go back to the apps list and confirm that the app you had idenitified is now **Unknown** again. 

 .. figure:: images/appdiscovery7.png

Takeaways
.........

- Prism Ultimate is our solution to being the gap between infrastructure and application and services layers. It covers the IT OPS process ranging from intelligent detection to automated remediation.

- X-FIT is our machine learning engine to support smart IT OPS, including capacity forecasting.

- X-Play, the IFTTT for the enterprise, is our engine to enable the automation of daily operations tasks, making it so easy that automation can be built by every admin.

- Prism Ultimate allows the admin to understand the relationship between their applications and infrastructure with broader visibility and intelligent insights learning. 

- X-Play can be used seamlessly with the Application data monitored via Prism Ultimate to build smart automation that can alert and remediate issues both on the infrastructure and on applications
