-------------------------------
Right-sizing VMs with Prism Pro
-------------------------------

.. figure:: images/operationstriangle.png

Prism Pro brings smart automation to our customer’s daily IT operations. The typical operations workflow is a continuous cycle of monitoring, analyzing and taking action where necessary. Prism Pro mirrors traditional IT Admin's workflows to improve operations efficiency. With Prism Pro, IT Admins are able to connect insights from machine data to automate this typical flow using the power of the machine learning engine X-FIT and the X-Play automation engine.

In this lab you will learn how Prism Pro can help IT Admins monitor, analyze and automatically act when a VM's memory resource is constrained.

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

Inefficiency Detection with Prism Pro X-FIT
+++++++++++++++++++++++++++++++++++++++++++

Prism Pro uses X-FIT machine learning to detect and monitor the behaviors of VMs running within the managed clusters.

Using machine learning, Prism Pro then analyzes the data and applies a classification to VMs that are learned to be inefficient. The following are short descriptions of the different classifications:

  * **Overprovisioned:** VMs identified as using minimal amounts of assigned resources.
  * **Inactive:** VMs that have been powered off for a period of time or that are running VMs that do not consume any CPU, memory, or I/O resources.
  * **Constrained:** VMs that could see improved performance with additional resources.
  * **Bully:** VMs identified as using an abundance of resources and affecting other VMs.

#. In **Prism Central**, select :fa:`bars` **> Dashboard** (if not already there).

#. From the Dashboard, take a look at the VM Efficiency widget. This widget gives a summary of inefficient VMs that Prism Pro’s X-FIT machine learning has detected in your environment. Click on the ‘View All Inefficeint VMs’ link at the bottom of the widget to take a closer look.

   .. figure:: images/ppro_58.png

#. You are now viewing the Efficiency focus in the VMs list view with more details about why Prism Pro flagged these VMs. You can hover the text in the Efficiency detail column to view the full description.

   .. figure:: images/ppro_59.png

#. Once an admin has examined the list of VM on the efficiency list they can determine any that they wish to take action against. From VMs that have too many or too little resources they will require the individual VMs to be resized. This can be done in a number of ways with a few examples listed below:

   * **Manually:** An admin edits the VM configuration via Prism or vCenter for ESXi VMs and changes the assigned resources.
   * **X-Play:** Use X-Plays automated play books to resize VM(s) automatically via a trigger or admins direction. There will be a lab story example of this later in this lab.
   * **Automation:** Use some other method of automation such as powershell or REST-API to resize a VM.


Increase Constrained VM Memory with X-Play based on Conitional Execution
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Now let’s look at how we can take automated action to resolve some of these inefficiencies. For this lab we will assume that this VM is constrained for memory, and will show how we can automatically remediate the right sizing of this VM. We will also use a custom ticket system to give an idea of how this typical workflow could integrate with ticketing system such as ServiceNow and use string parsing and conditional execution, two of our latest capabilities added into X-Play. 

Prism Pro now also has the ability to import and export playbooks. The steps to do so for the second playbook created below are listed in the next section. You will need to complete the rest of the steps such as setting up the alert policy and stressing the VM but if you understand how playbooks function and can be created easily you can leverage the file provided in the next section and follow the steps to save some time. We recommend reading through the steps to create trhe playbook and understanding them properly. 

#. Navigate to your **`Initials`-LinuxToolsVM**. The examples will use a VM called **ABC - LinuxToolsVM**. Note the current **Memory Capacity** of the VM, as we will later increase it with X-Play. You may need to scroll down within the **Properties** widget to find this value.

   .. figure:: images/linuxvm.png

#. Using the hamburger menu, navigate to **Operations** > **Playbooks**.

   .. figure:: images/navigateplaybook.png

#. We will need to create a couple of Playbooks for this workflow to be possible. Let's start by clicking **Create Playbook**. We will first be creating the Playbook that will be increasing the Memory of the VM. We want to create a playbook that reads in a string coming from the ticket system (approved or denied in our case) and have conditional branching and execution of the next steps accordingly. 

   .. figure:: images/rs3b.png

#. Select **Webhook** as the trigger. Using this trigger exposes a public API that allows scripts and third party tools such as ServiceNow to use this Webhook to call back into Prism Central and trigger this playbook. In our case, this Playbook will be called by the ticket system to initiate conditional execution.

   .. figure:: images/rs16.png

#. Click the **Add Action** item on the left side.

   .. figure:: images/rs17.png

#. The first action we will add is the newly added String Parse action. This action allows the user to parse data coming from a string which can then subsequently be used in the succeeding actions. 

   .. figure:: images/addparse.png

#. Use the **Parameters** link to fill in the **string5** parameter exposed from the webhook trigger. In our example this will be the condition passed in from the API call. We have the format options for JSON, XML and Regex. This example we’ll use a JSON path. Fill in the other fields according to the screen below. Then click **Add Action** to add the next action.

   .. figure:: images/editparse.png

#. Now we’ll add our first condition - Select the **Branch** action. This gives the ability to execute succeeding actions based on coditions and criteria matched.

   .. figure:: images/addbranch.png

#. We will use the **IF** condition and choose our Operand as the **Parsed String** from the previous action using the **Parameters** link. Fill in the other fields according to the screen below. We can also add a description to the branch action for easier readability. Next we'll add the actions we want to execute if the condition is true. Click add **Add Action** once you have filled the fields for the **Branch** action.

   .. figure:: images/editbranch.png

#. First action we want to take is add memory to the VM. Select the **VM Add Memory** action. Use the **Parameters** link to fill in the **entity1** parameter which is exposed from the Webhook trigger. The caller will pass in the VM to act on as entity1. Set the remainder of the fields according to the screen below. Then click **Add Action** to add the next action.

   .. figure:: images/addmemory.png

#. Select the **Resolve Alert** action. Use the **Parameters** link to fill in the **entity2** parameter which is exposed from the Webhook trigger. The caller will pass the Alert to be resolved as entity2. Then click **Add Action** and choose the **Email** action.

   .. figure:: images/resolvealert.png

#. Fill in the field in the email action. Here are the examples.

   - **Recipient:** - Fill in your email address.
   - **Subject:** - ``Playbook {{playbook.playbook_name}} was executed.``
   - **Message:** - ``{{playbook.playbook_name}} has run and has added 1GiB of Memory to the VM {{trigger[0].entity1.name}}.``

   .. note::

      You are welcome to compose your own subject message. The above is just an example. You could use the “parameters” to enrich the message.

   .. figure:: images/approvedemail.png

#. Now, we would like to call back to the ticket service to resolve the ticket in the ticket service. Click **Add Action** to add the **REST API** action. Fill in the following values replacing the <PrismOpsLabUtilityServer_IP_ADDRESS> in the URL field. This condcludes our first conditional branch for an approved request.

   - **Method:** PUT
   - **URL:** http://<PrismOpsLabUtilityServer_IP_ADDRESS>/resolve_ticket
   - **Request Body:** ``{"incident_id":"{{trigger[0].entity1.uuid}}"}``
   - **Request Header:** Content-Type:application/json;charset=utf-8

   .. figure:: images/resolveticket.png

#. Next we’ll add the 2nd condition for when the request is denied. Click **Add Action** and choose the **Branch** action. We will use the **Else** condition. We could also add **Else If** we wanted to use other operands. For now we’ll use just Else. We can also add a description for the Branch. 

   .. figure:: images/elsebranch.png

#. On this condition we just want to send out an email notifying the user that the request has been denied and the memory was not added. Click **Add Action** and choose the **Email** action. Fill in the field in the email action. Here is an example.

   - **Recipient:** - Fill in your email address.
   - **Subject:** - ``Memory Increase Request Denied``
   - **Message:** - ``The request to increase the memory of your VM {{trigger[0].entity1.name}} by 1 GB was denied. If you'd like to review the ticket please navigate to http://<PrismOpsLabUtilityServer_IP_ADDRESS>/ticketsystem``

   .. figure:: images/deniedemail.png

#. Click **Save & Close** button and save it with a name “*Initials* - Resolve Service Ticket”. **Be sure to enable the ‘Enabled’ toggle.**



#. Next we will create a custom action to be used in our 2nd playbook. Click on **Action Gallery** from the left hand side menu. Alternatively, you can skip to the next section to import the playbook needed for this part. You **Will** need to complete the rest of the steps to trigger the workflow. 

   .. figure:: images/rs3c.png

#. Select the **REST API** action and choose the **Clone** operation from the actions menu.

   .. figure:: images/rs4.png

#. Fill in the following values replacing your initials in the *Initials* part, and the <PrismOpsLabUtilityServer_IP_ADDRESS> in the URL field. Click **Copy**.

   - **Name:** *Initials* - Generate Service Ticket
   - **Method:** POST
   - **URL:** http://<PrismOpsLabUtilityServer_IP_ADDRESS>/generate_ticket/
   - **Request Body:** ``{"vm_name":"{{trigger[0].source_entity_info.name}}","vm_id":"{{trigger[0].source_entity_info.uuid}}","alert_name":"{{trigger[0].alert_entity_info.name}}","alert_id":"{{trigger[0].alert_entity_info.uuid}}", "webhook_id":"<ENTER_ID_HERE>","string1":"Request 1GiB memory increase."}``
   - **Request Header:** Content-Type:application/json;charset=utf-8

   .. figure:: images/rs5.png

#. Now switch to the Playbooks list by clicking the **List** item in the left hand menu.

   .. figure:: images/rs6.png

#. We will need to copy the Webhook ID from the first Playbook we created so that it can be passed in the generate ticket step. Open up your Resolve Service Ticket playbook and copy the Webhook ID to your clipboard.

   .. figure:: images/webhookid.png

#. Now we will create a Playbook to automate the generation of a service ticket. Close your Playbook and then click **Create Playbook** at the top of the table view.

   .. figure:: images/rs7.png

#. Select **Alert** as a trigger

   .. figure:: images/rs8.png

#. Search and select **VM {vm_name} Memory Constrained** as the alert policy, since this is the issue we are looking to take automated steps to remediate.

   .. figure:: images/rs9.png

#. Select the *Specify VMs* radio button and choose the VM you created for the lab. This will make it so only alerts raised on your VM will trigger this Playbook.

   .. figure:: images/selectvm.png

#. First, we would like to generate a ticket for this alert. Click **Add Action** on the left side and select the **Generate Service Ticket** action you created. Notice the details from the **Generate Service Ticket** Action you created are automatically filled in for you. Go ahead and replace the **<ENTER_ID_HERE>** text with the Webhook ID you copied to your clipboard.

   .. figure:: images/serviceticket.png

#. Next we would like to notify someone that the ticket was created by X-Play. Click **Add Action** and select the Email action. Fill in the field in the email action. Here are the examples. Be sure to replace <PrismOpsLabUtilityServer_IP_ADDRESS> in the message with it's IP Address.

   - **Recipient:** - Fill in your email address.
   - **Subject :** - ``Service Ticket Pending Approval: {{trigger[0].alert_entity_info.name}}``
   - **Message:** - ``The alert {{trigger[0].alert_entity_info.name}} triggered Playbook {{playbook.playbook_name}} and has generated a Service ticket for the VM: {{trigger[0].source_entity_info.name}} which is now pending your approval. A ticket has been generated for you to take action on at http://<PrismOpsLabUtilityServer_IP_ADDRESS>/ticketsystem``

   .. figure:: images/rs13.png

#. Click **Save & Close** button and save it with a name “*Initials* - Generate Service Ticket for Constrained VM”. **Be sure to enable the ‘Enabled’ toggle.**

   .. figure:: images/rs14.png

#. Now let's trigger the workflow. Navigate to the tab you opened in the setup with the **/alerts** URL [example 10.38.17.12/alerts]. Select the Radio for **VM Memory Constrained** and input your VM. Click the **Simulate Alert** button. This will simulate a memory constrained alert on your VM.

   .. figure:: images/alertsimulate.png

#. You should recieve an email to the email address you put down in the first playbook. It may take up to 5 minutes.

   .. figure:: images/ticketemail.png

#. Inside the email click the link to visit the ticket system. Alternatively you can directly access the ticket system by navigating to http://`<PrismOpsLabUtilityServer_IP_ADDRESS>`/ticketsystem from a new tab in your browser.

   .. figure:: images/ticketsystem.png

#. Identify the ticket created for your VM, and click the vertical dots icon to show the Action menu. Click the **Deny** option. This will call the Webhook that was passed in the REST API to generate the service ticket, which will trigger the Resolve Service Ticket Playbook. It will pass on the condition for branching action and execute the **Denied** workflow. You should receive an email within a few minutes with the message input for this condition.

   .. figure:: images/ticketoption.png


#. Switch back to the previous tab with the Prism Central console open. Open up the details for the **`Initials` - Resolve Service Ticket** Playbook and click the **Plays** tab towards the top of the view to take a look at the Plays that executed for this playbook. The sections in this view can be expanded by clicking to show more details for each item. If there were any errors, they would also be surfaced in this view. You can click on the **String Parser** action to confirmt that the right condition was passed in from the webhook.

   .. figure:: images/deniedplay.png


#. Now navigate back to the ticket system either using the link in the denied email or going directly to http://`<PrismOpsLabUtilityServer_IP_ADDRESS>`/ticketsystem. Identify the ticket created for your VM, and click the vertical dots icon to show the Action menu. Click the **Approve** option. This will call the Webhook that was passed in the REST API to generate the service ticket, which will trigger the Resolve Service Ticket Playbook. It will pass on the condition for branching action and execute the **Approved** workflow. It will also pass on the information for the VM and Alert that triggered the workflow so the following actions to add memory and resolve alert are also executed. 

   .. figure:: images/ticketoption.png

#. Switch back to the previous tab with the Prism Central console open. Open up the details for the **`Initials` - Resolve Service Ticket** Playbook and click the **Plays** tab towards the top of the view to take a look at the Plays that executed for this playbook. The sections in this view can be expanded to show more details for each item. If there were any errors, they would also be surfaced in this view. You can click on the **String Parser** action to confirmt that the right condition was passed in from the webhook.

   .. figure:: images/approvedbranch.png

#. You can navigate back to your VM and verify that the Memory was indeed increased by 1 GiB.

   .. figure:: images/finalmemory.png

#. You should also get an email telling you that the playbook ran.

   .. figure:: images/successemail.png

Importing/Exporting Playbooks
+++++++++++++++++++++++++++++++++++++++++++

X-Play now has the ability to import and export playbooks across Prism Centrals. In the example below we will show how to import the playbook that is created in the preceding steps. The user will still need to create the alert policies and go through the workflow to trigger the alert as listed in the steps in the previous section.

#. Go to Playbooks page and click on **Import** 

 .. figure:: images/import0.png

#. You will need to choose the Binary file that you downloaded as the playbook to import. 

 .. figure:: images/import1.png

#. You will see some validation errors since the certain fields such as credentials and URLs will be different for your environment. Click on **Import**, we will resolve these errors in the next step.

 .. figure:: images/import2.png

#. Click on the playbook that has just been imported for you - there will be a time stamp in the playbook name. Once open the you will see that the actions that have validation errors have been highlighted. Even for actions that have not been highlighted make sure to confirm that the information such as **Passwrods**, **URLs** and **IP Addresses** is correct according to your environment. Refer to the playbook creation steps above to confirm these fields. Once you have changed these fields click on **Save & Close**. If validation errors are still present, the pop-up will say so. otherwise remember to click **Enable** and add your Initials to the playbook name before clicking **Save**

 .. figure:: images/rsimport1.png


Takeaways
.........

- Prism Pro is our solution to make IT OPS smarter and automated. It covers the IT OPS process ranging from intelligent detection to automated remediation.

- X-FIT is our machine learning engine to support smart IT OPS, including anomaly detection, and inefficiency detection.

- X-Play enables admins to confidently automate their daily tasks within minutes.

- X-Play is extensive that can use customer’s existing APIs and scripts as part of its Playbooks, and can integrate nicely with customers existing ticketing workflows.

- X-Play can enable automation of daily operations tasks with a complete IFTTT workflow thanks to conditional execution.
