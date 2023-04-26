# Invoice Data Extraction - Python Example

## What will we create?

This tutorial will guide us in building a simple invoice data extraction process using a Temporal.io worker workflow (*when we apply the Workflow as Code paradigm*), Python, the PyTesseract library for OCR, and a single invoice model to facilitate the use case of the example, to then display the data obtained on the screen.


## Prerequisites

Before starting your workflow for the first time, you must register in [KuFlow (app.kuflow.com)](https://app.kuflow.com/). After familiarizing yourself with the user interface by navigating through the menus or visiting our [Youtube channel](https://www.youtube.com/channel/UCXoRtHICa86YfX8P_wu1f6Q) with many videos that will help you in this task, you are ready to perform the necessary configurations for our Worker. To do so, click on the `Management` menu.

### Create the Credentials

#### Create the credentials for the Worker

We will configure an `APPLICATION` that will provide us with the necessary credentials so that the worker (written in Java, TypeScript, or Python and located in your own machine) can interface with KuFlow.

Go to the `Settings > Applications` menu and click on `Add application`. We establish the name we want and save. Next, you will get the first data needed to configure our Worker.

- **Identifier**: Unique identifier of the application. For this tutorial: *myApp*
  - Later in this tutorial, we will configure it in the `kuflow.api.client-id` property of our example.
- **Token**: Password for the application.
  - Later in this tutorial, we will configure it in the `kuflow.api.client-secret` property of our example.
- **Namespace**: Temporal's namespace.
  - Later in this tutorial, we will configure it in the `application.temporal.namespace` property of our example.

Next, we will proceed to create the certificates that will serve us to configure the Mutual TLS with which our Worker will perform the authentication against Temporal. To do this we click on "Add certificate", set the name we want, and choose the `PKCS8` type for the encryption of the private key. This is important since the example code in this tutorial works with this encoding. We will get the following:

- **Certificate**: It is the public part that is presented in the *mTLS* connection.
  - Later in this tutorial, we will configure it in the `application.temporal.mutual-tls.cert-data` property of our example.
- **Private Key**: It is the private key for *mTLS*.
  - Later in this tutorial, we will configure it in the `application.temporal.mutual-tls.key-data` property of our example.

It is also necessary to indicate the CA certificate, which is the root certificate with which all certificates are issued. It is a public certificate and for convenience you can find it in the same `Application` screen, under the name of *CA Certificate*. This certificate will always be the same between workers.

- **CA Certificate**: Root certificate with which all certificates (client and server certificates) are issued.
  - Later in this tutorial, we will configure it in the `kuflow.activity.kuflow.key-data` property of our example.

Finally, you get something like:

<div class="text--center">

![](/img//App.png)

</div>

## Preparing Scenario

### Invoice example

As we said in the introduction, we are starting from the assumption that we are constantly dealing with the same types of invoices (*from the same supplier*) and will use a pre-built invoice, which you can download from [**here**](https://github.com/Hec-KuFlow/KuFlow-ExtractInvoiceData/blob/main/invoice_1.jpg). Keep in mind we have created some regular expressions based on it; if you use another invoice, please modify the text search methods and RegEx according to it.

### Create the process definition

We need to create the definition of the process that will execute our workflow. In this section, we will configure the KuFlow tasks of which it is made up as well as the information necessary to complete said tasks, the process access rules (i.e. *RBAC*), as well as another series of information. To do this we go to the `Setting > Processes` menu and create a new process.

Complete *Process Definition* with the (*recommended*) following data:

- **Process name**
    - Invoice Data Extract
- **Description**
    - Free text description about the Workflow.
- **Workflow**
    - **Workflow Engine**
   	 - *KuFlow Engine*, because we are designing a Temporal-based Worker.
  - **Workflow Application**
  		- myApp, the application to which our Worker will connect to.
    - **Task queue**
   	 - The name of the Temporal queue where the KuFlow tasks will be set. You can choose any name, later you will set this same name in the appropriate configuration in your Worker. For this tutorial: *IDEQueue*.
    - **Type**
   	 - It must match the name of the Java interface of the Workflow. For this tutorial, *IDEWorker* is the name you should type in this input.
- **Permissions**
    - At least one user or group of users must have the role of `INITIATOR` to instantiate the process through the application. In this tutorial, we will allow "Users" (*Default Group*) from this organization.

Finally, you get something like:

<div class="text--center">

![](/img/TUT14-03-Process.png)

</div>

We will define five **Task Definition** in the process as follows:

- Task one **"Invoice Upload"**
    - **Description:** Free text description about the Task.
    - **Code:** FILEUPLOAD_TASK
    - **Permissions:** 
    	- **Users**  (*The "Default Group". Because in this tutorial we will allow all users from this organization to complete/watch this activity*)
    		- **Role:** Candidate
    - **Elements:**
   	 - **Name:** File to Upload
   		 - **Description:** Free text description about the element (*optional*).
   		 - **Code:** uploadedFile
   		 - **Type:** Document
   		 - **Properties:** Mandatory

You'll get something like:

<div class="text--center">

![](/img/TUT14-04-Task.png)

</div>

**NOTE** The following task will be an informative one; due to this, there are no elements needed.
 
- Task two **"File Processing"**
    - **Description:** Free text description about the Task.
    - **Code:** FILEPROCESS_TASK
    - **Permissions:**
    	- **Users**  (*The "Default Group". Because in this tutorial we will allow all users from this organization to complete/watch this activity*)
    		- **Role:** Viewer
    	- **myApp**  
    		- **Role:** Candidate
    - **No Elements**

You'll get something like:

<div class="text--center">

![](/img/TUT14-04-Task2.png)

</div>

**NOTE** In the following task, we will not mark the text fields as "read only", since we will give the user the possibility of modification.
 
- Task three **"Data Validation"**
    - **Description:** Free text description about the Task.
    - **Code:** DATAVALIDATION_TASK
 - **Permissions:**
    	- **Users**  (*The "Default Group". Because in this tutorial we will allow all users from this organization to complete/watch this activity*)
    		- **Role:** Viewer, Candidate
    	- **myApp**  
    		- **Role:** Candidate
    - **Elements:**
   	 - **Name:** Client Name
   		 - **Description:** Free text description about the element (*optional*).
   		 - **Code:** clientName
   		 - **Type:** Field
   		 - **Field Type:** Text
   	 - **Name:** Invoice ID
   		 - **Description:** Free text description about the element (*optional*).
   		 - **Code:** invoiceID
   		 - **Type:** Field
   		 - **Field Type:** Text
   	 - **Name:** Invoice Date
   		 - **Description:** Free text description about the element (*optional*).
   		 - **Code:** invoiceDate
   		 - **Type:** Field
   		 - **Field Type:** Text
   	 - **Name:** Total
   		 - **Description:** Free text description about the element (*optional*).
   		 - **Code:** grandTotal
   		 - **Type:** Field
   		 - **Field Type:** Text
   	 - **Name:** Confirm Processing?
   		 - **Description:** Free text description about the element (*optional*).
   		 - **Code:** confirmation
   		 - **Type:** Decision
   		 - **Properties:** Mandatory   		 
   		 - **Values:** Mandatory
 		 	- **Code:** YES **Name:** Yes
 		 	- **Code:** NO **Name:** No
   	 - **Name:** Comments
   		 - **Description:** Free text description about the element (*optional*).
   		 - **Code:** comments
   		 - **Type:** Field
   		 - **Field Type:** Text

You'll get something like:

<div class="text--center">

![](/img/TUT14-04-Task3.png)

</div>

**NOTE** The following task will be an informative one; due to this, there are no elements needed.
 
- Task four **"Invoice Processing"**
    - **Description:** Free text description about the Task.
    - **Code:** INVOICEPROCESS_TASK
    - **Permissions:**
    	- **Users**  (*The "Default Group". Because in this tutorial we will allow all users from this organization to complete/watch this activity*)
    		- **Role:** Viewer
    	- **myApp**  
    		- **Role:** Candidate
    - **No Elements**

You'll get something like:

<div class="text--center">

![](/img/TUT14-04-Task4.png)

</div>

**NOTE** The next task will emulate the response of an external system, which can be any of your environments, that processes the invoice information and provides a response to our worker.
 
- Task five: **"Processing Response"**
    - **Description:** Free text description about the Task.
    - **Code:** RESPONSE_TASK
    - **Permissions:**
    	- **Users**  (*The "Default Group". Because in this tutorial we will allow all users from this organization to complete/watch this activity*)
    		- **Role:** Viewer
    	- **myApp**  
    		- **Role:** Candidate
    - **No Elements**

You'll get something like:

<div class="text--center">

![](/img/TUT14-04-Task5.png)

</div>


### Publish the process and download the template for the Workflow Worker

By clicking on the `Publish` button you’ll receive a confirmation request message, once you have confirmed, the process will be published.

<div class="text--center">

![](/img/TUT14-05-publish_1.png)

![](/img/TUT14-05-publish_2.png)

</div>

Now, you can download a sample Workflow Implementation from the Process Definition main page.

<div class="text--center">

![](/img/TUT14-07-Template_1.png)

![](/img/TUT14-07-Template_2.png)

</div>

### Main technologies used in the example

The following technologies have been mainly used in our example:

- **Operating System:** Microsoft Windows 11 Professional
- **IDE:** Visual Studio Code 
  - You can use *IntelliJ Idea*, *Eclipse*, *PyCharm*, *Atom*, *WebStorm*, or any other with corresponding language plugins.
- **Python (>=3.8)**
- **Poetry (>=1.3.2)**
  - For python packaging and dependency management
- **KuFlow Python SDK**
  - Provide some activities and utilities to work with KuFlow.
- **Temporal Python SDK**
  - To perform GRPC communications with the KuFlow temporal service.


## Implementation

This code will serve as a starting point for implementing our application worker. 

**Note:** You can download the following project from our [Community Github repository](https://github.com/Hec-KuFlow)

### Create the Virtual Environment and resolve dependencies

Once you have unzipped the template, open it and, on a new terminal window in your IDE, execute the following commands:

- **poetry new extract-invoice-data**
  - Or provide the name you want.
- **poetry install**
  - To download all dependencies needed.

### Using Credentials

Now, in this step we are filling up the application configuration information. You must complete all the settings and replace the example values indicated as "FILL_ME".

#### KuFlow’s Credentials

The appropriate values can be obtained from the KuFlow application. Check out the [Create the Credentials](#create-the-credentials-for-the-worker) section of this tutorial.

```yaml
# ===================================================================
# PLEASE COMPLETE ALL CONFIGURATIONS BEFORE STARTING THE WORKER
# ===================================================================

kuflow:
 api:

   # ID of the APPLICATION configured in KUFLOW.
   # Get it in "Application details" in the Kuflow APP.
   client-id: FILL_ME

   # TOKEN of the APPLICATION configured in KUFLOW.
   # Get it in "Application details" in the Kuflow APP.
   client-secret: FILL_ME

application:
 temporal:

   # Temporal Namespace. Get it in "Application details" in the KUFLOW APP.
   namespace: FILL_ME

   # Temporal Queue. Configure it in the "Process definition" in the KUFLOW APP.
   kuflow-queue: FILL_ME

   mutual-tls:
   # Client certificate
   # Get it in "Application details" in the KUFLOW APP.
   cert-data: |
   	-----BEGIN CERTIFICATE-----
   	fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_
   	fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_
   	…
   	fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_
   	fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_
   	-----END CERTIFICATE-----

   # Private key
   # Get it in "Application details" in the KUFLOW APP.
   # IMPORTANT: This example works with PKCS8, so ensure PKCS8 is selected
   #        	when you generate the certificates in the KUFLOW App
   key-data: |
   	-----BEGIN CERTIFICATE-----
   	fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_
   	fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_
   	…
   	fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_
   	fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_
   	-----END CERTIFICATE-----

   # KUFLOW Certification Authority (CA) of the certificates issued in KUFLOW
   ca-data: |
   	-----BEGIN CERTIFICATE-----
   	fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_
   	fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_
   	…
   	fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_
   	fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_fill_me_
   	-----END CERTIFICATE-----
```

Please note that this is a YAML, respect the indentation. You'll get something like this:

<div class="text--center">

![](/img/Template_3.png)

</div>

### Define new activities

We create a new file called **activities.py** which is an example set of activities; here you should write your own implementation. Feel free to use it as a base and modify it at your convenience; otherwise, *Remember* You can download this project from our [Community Github repository](https://github.com/Hec-KuFlow).

It will have the necessary code to perform the following actions:

- Define two dataclasses to hold the request and response data
- Define a class to hold the activity methods
	- Initialize the class with a KuFlowRestClient instance
	- Define an activity method to extract invoice data from an image
		- Retrieve the task from KuFlow and get the uploaded document
		- Download the document and convert it into an image
		- Extract data from the image and get the final data
		- Return the final data as a response
	- Define a method to extract invoice data from an image using pytesseract
	- Define a method to extract a substring from a string between two words
	- Define a method to get the final invoice data from the extracted data

Since we are going to use two particular libraries for this example, we must add them to our project. For this, we will execute the following commands in a terminal:

- **poetry add pillow**
- **poetry add pytesseract**

```python
#
# Copyright (c) 2023-present KuFlow S.L.
#
# All rights reserved.
#

from dataclasses import dataclass
import re
import io
import pytesseract
from PIL import Image
from temporalio import activity
from kuflow_rest import KuFlowRestClient
from kuflow_rest import models


# Define two dataclasses to hold the request and response data
@dataclass
class InvoiceDataExtractionRequest:
    task_id: str


@dataclass
class InvoiceDataExtractionResponse:
    client: str
    invoice_number: str
    invoice_date: str
    invoice_total: str


# Define a class to hold the activity methods
class InvoiceActivities:
    # Initialize the class with a KuFlowRestClient instance
    def __init__(self, kuflow_client: KuFlowRestClient) -> None:
        self._kuflow_client = kuflow_client
        self.activities = [self.invoice_data_extraction]

    # Define an activity method to extract invoice data from an image
    @activity.defn
    async def invoice_data_extraction(self, request: InvoiceDataExtractionRequest) -> InvoiceDataExtractionResponse:
        # Retrieve the task from KuFlow and get the uploaded document
        task = self._kuflow_client.task.retrieve_task(id=request.task_id)
        document: models.TaskElementValueDocument = task.element_values["uploadedFile"][0]

        # Download the document and convert it into an image
        document_file = (
            self._kuflow_client.task.actions_task_download_element_value_document(
                id=request.task_id, document_id=document.value.id)
        )
        byte_data = b"".join(document_file)
        binary_stream = io.BytesIO(byte_data)
        image = Image.open(binary_stream)

        # Extract data from the image and get the final data
        data_extracted = self.extract_invoice_data(image)
        final_data = self.get_final_data(data_extracted)

        # Return the final data as a response
        return InvoiceDataExtractionResponse(
            client=final_data[0],
            invoice_number=final_data[1],
            invoice_date=final_data[2],
            invoice_total=final_data[3],
        )

    # Define a method to extract invoice data from an image using pytesseract
    def extract_invoice_data(self, image):
        pytesseract.pytesseract.tesseract_cmd = (r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        invoice_data = pytesseract.image_to_string(image)
        return invoice_data

    # Define a method to extract a substring from a string between two words
    def get_text_between(self, main_string, start_word, end_word):
        start = main_string.find(start_word) + len(start_word)
        end = main_string.find(end_word)
        return main_string[start:end]

    # Define a method to get the final invoice data from the extracted data
    def get_final_data(self, data):
        patron_fecha = r"\b\d{1,2}/\d{1,2}/\d{4}\b"
        patron_total = r"\bTOTAL\D*(\d+(?:[,.]\d+)?)(?:\s*(?:€|\$|USD|EUR))?\b"

        client = self.get_text_between(data, "www.quiasmoeditorial.es", "C/ ").strip()
        invoice_number = self.get_text_between(data, "Factura ", " |").strip()

        invoice_date = re.search(patron_fecha, data).group(0)
        invoice_total = re.findall(patron_total, data)[1]

        return client, invoice_number, invoice_date, invoice_total
```

**NOTE**  You will find a file called "[*standalone_activities.py*](https://github.com/Hec-KuFlow/KuFlow-ExtractInvoiceData/blob/main/standalone_activities.py)", which is the code that works outside this project in a stand-alone environment, to illustrate the changes it will receive to work in a KuFlow environment.

### Register Activities

In order to register the recently created activity in our application worker, we must modify **worker.py** as follows:

With **HERE** and some description before each line we'll highlight new code.

Near the end of the file:

```python

 	...

	# Important. Do not forget.
	# Start in background, the auto-renewal of the Temporal.io connection token.
	kuflow_authorization_token_provider.start_auto_refresh(client)

	# Initializing KuFlow Temporal.io activities
	kuflow_sync_activities = KuFlowSyncActivities(kuflow_client)
	kuflow_async_activities = KuFlowAsyncActivities(kuflow_client)
	# HERE: Add to register the activity, your IDE will import the activity
	invoice_activities = InvoiceActivities(kuflow_client)

	# Temporal Worker initialization
	worker = Worker(
    	client,
    	task_queue=temporal_queue,
    	workflows=[SampleWorkflow],
    	activities=kuflow_sync_activities.activities
    	+ kuflow_async_activities.activities
    	# HERE: Add "+ invoice_activities.activities,"
    	+ invoice_activities.activities,
    	workflow_runner=UnsandboxedWorkflowRunner()
	)

	...

```

**NOTE** If your IDE doesn't resolve the import, add "from worker_sample.activities import InvoiceActivities" in the imports section.

### Workflow Implementation

In this section, we will modify the **workflow.py** file to make the fundamental steps to creating the most basic workflow for this business process:

- Users in the organization could upload a new invoice file, and the automatic process will detect some information from it, such as Client Name, Invoice Number, Invoice Date and Grand Total, and display it on KuFlow's UI. Then, if the user gives approval, it will be processed by an external system, which will return an operation number.

To make this part of the tutorial more understandable, we are going to explain, part by part, what modifications we make, initially dividing them into tasks keeping the workflow order. A small clarification: in the template, each task is assumed to be asynchronous, which means that it will wait for a response, for example from a user, from the interface. If we want to automate the task, we must convert it to synchronous.

With **HERE** and some description before each line we'll highlight new code.

#### Task One: Upload File (create_task_invoice__upload)

At the end of this asynchronous task, we add a "return id" line for further reference of the task and later obtain the file that was uploaded to it by the user.

```python

    async def create_task_invoice__upload(self, processId: str):
        """Create task "Invoice Upload" in KuFlow and wait for its completion"""

        id = workflow.uuid4()

        task_definition = models.TaskDefinitionSummary(code=self.TASK_CODE_INVOICE_UPLOAD)
        task = models.Task(id=id, process_id=processId, task_definition=task_definition)

        await workflow.execute_activity(
            KuFlowAsyncActivities.create_task_and_wait_finished,
            models_temporal.CreateTaskRequest(task=task),
            start_to_close_timeout=self._kuflow_activity_async_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_async_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        # HERE: Add the following line to return the task id to be used in the activity
        return id

```

#### Task Two: File Processing (create_task_file__processing)

As we said before, we have to convert this activity to synchronous.

First, we add the variable "upload_task_id: str" as an argument, which will receive the id of the file upload task (task one).

The code has been modified to add new functionality. The original code is an Asynchronous task waiting for its completion. The new code changes to Synchronous and adds the ability to claim and complete the task, as well as to execute an additional activity called "InvoiceActivities.invoice_data_extraction".

To do this, several new sections have been added to the code:

- The first new section modifies the activity to create the task using KuFlowSyncActivities.create_task instead of KuFlowAsyncActivities.create_task_and_wait_finished.
- The second new section executes the activity to claim the task using KuFlowSyncActivities.claim_task.
- The third new section executes a progress message on the Kuflow interface using KuFlowSyncActivities.append_task_log.
- The fourth new section executes the activity "InvoiceActivities.invoice_data_extraction", which performs our OCR and extracts the invoice information.
- The fifth new section executes a progress finished message on the Kuflow interface using KuFlowSyncActivities.append_task_log.
- The last new section executes the activity to complete the task using KuFlowSyncActivities.complete_task.

Finally, the function also returns a response of type InvoiceDataExtractionResponse, which is the result of the "InvoiceActivities.invoice_data_extraction" activity.

```python

    async def create_task_file__processing(self, processId: str, upload_task_id: str) -> InvoiceDataExtractionResponse:
        """Create task "File Processing" in KuFlow and wait for its completion"""

        id = workflow.uuid4()

        task_definition = models.TaskDefinitionSummary(code=self.TASK_CODE_FILE_PROCESSING)
        task = models.Task(id=id, process_id=processId, task_definition=task_definition)

        # HERE: Modify the activity to create the task using KuFlowSyncActivities.create_task
        await workflow.execute_activity(
            KuFlowSyncActivities.create_task,
            models_temporal.CreateTaskRequest(task=task),
            start_to_close_timeout=self._kuflow_activity_async_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_async_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        # HERE: Add this section to execute the activity to claim the task using KuFlowSyncActivities.claim_task
        await workflow.execute_activity(
            KuFlowSyncActivities.claim_task,
            models_temporal.ClaimTaskRequest(taskId=id),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        # HERE: Add this section to execute a progress message on the Kuflow interface
        await workflow.execute_activity(
            KuFlowSyncActivities.append_task_log,
            models_temporal.AppendTaskLogRequest(taskId=id, log=models.Log(message="Processing File", level=models.LogLevel.INFO),),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        # HERE: Add this section to execute the task "invoice_data_extraction" from the activity
        final_data = await workflow.execute_activity(
            InvoiceActivities.invoice_data_extraction,
            InvoiceDataExtractionRequest(task_id=upload_task_id),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        # HERE: Add this section to execute a progress finished message on the Kuflow interface
        await workflow.execute_activity(
            KuFlowSyncActivities.append_task_log,
            models_temporal.AppendTaskLogRequest(taskId=id, log=models.Log(message="File Processed", level=models.LogLevel.INFO),),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        # HERE: Add this section to executes the activity to complete the task using KuFlowSyncActivities.complete_task
        await workflow.execute_activity(
            KuFlowSyncActivities.complete_task,
            models_temporal.CompleteTaskRequest(taskId=id),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        # HERE: Add the following line to return the response from the activity
        return final_data

```

#### Task Three: Data Validation (create_task_data__validation)

First, we add the variable "final_data: InvoiceDataExtractionResponse" as an argument, which will receive the data from the file processing task (task two).

The changes made to this piece of code involve setting values for some task elements before creating and executing the task. Specifically, four elements for buyer name, invoice ID, invoice date, and grand total are set with values extracted from the final_data object.

In the new code, the task.element_values attribute is set with a dictionary containing the four elements and their corresponding values extracted from final_data. This dictionary is then passed to execute_activity() along with the other arguments.

The effect of these changes is that when the task is executed, it will have element values set for buyer name, invoice ID, invoice date, and grand total, which will be available to downstream activities or workflows. 

```python

    async def create_task_data__validation(self, processId: str, final_data: InvoiceDataExtractionResponse):
        """Create task "Data Validation" in KuFlow and wait for its completion"""

        id = workflow.uuid4()

        task_definition = models.TaskDefinitionSummary(code=self.TASK_CODE_DATA_VALIDATION)
        task = models.Task(id=id, process_id=processId, task_definition=task_definition)

        # HERE: Set element values of the task for buyer name, invoice ID, invoice date and grand total
        task.element_values = {}
        task.element_values["buyerName"] = [models.TaskElementValueString(value=final_data.client)]
        task.element_values["invoiceID"] = [models.TaskElementValueString(value=final_data.invoice_number)]
        task.element_values["invoiceDate"] = [models.TaskElementValueString(value=final_data.invoice_date)]
        task.element_values["grandTotal"] = [models.TaskElementValueString(value=final_data.invoice_total)]

        await workflow.execute_activity(
            KuFlowAsyncActivities.create_task_and_wait_finished,
            models_temporal.CreateTaskRequest(task=task),
            start_to_close_timeout=self._kuflow_activity_async_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_async_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

```

#### Task Four: Invoice Processing (create_task_invoice__processing)

The original code is an Asynchronous task waiting for its completion. The new code changes to Synchronous and adds the ability to claim, log, and complete the task, like the second task, with the difference that here we don't execute any activity.


```python

    async def create_task_invoice__processing(self, processId: str):
        """Create task "Invoice Processing" in KuFlow and wait for its completion"""

        id = workflow.uuid4()

        task_definition = models.TaskDefinitionSummary(code=self.TASK_CODE_INVOICE_PROCESSING)
        task = models.Task(id=id, process_id=processId, task_definition=task_definition)

        # HERE: Modifiy the activity to create the task using KuFlowSyncActivities.create_task
        await workflow.execute_activity(
            KuFlowSyncActivities.create_task,
            models_temporal.CreateTaskRequest(task=task),
            start_to_close_timeout=self._kuflow_activity_async_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_async_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        # HERE: Add this section to execute the activity to claim the task using KuFlowSyncActivities.claim_task
        await workflow.execute_activity(
            KuFlowSyncActivities.claim_task,
            models_temporal.ClaimTaskRequest(taskId=id),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        # HERE: Add this section to execute a progress message on the Kuflow interface
        await workflow.execute_activity(
            KuFlowSyncActivities.append_task_log,
            models_temporal.AppendTaskLogRequest(taskId=id, log=models.Log(message="Processing File", level=models.LogLevel.INFO),),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        # HERE: Add this section to execute a progress finished message on the Kuflow interface
        await workflow.execute_activity(
            KuFlowSyncActivities.append_task_log,
            models_temporal.AppendTaskLogRequest(taskId=id, log=models.Log(message="File Processed", level=models.LogLevel.INFO),),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        # HERE: Add this section to executes the activity to complete the task using KuFlowSyncActivities.complete_task
        await workflow.execute_activity(
            KuFlowSyncActivities.complete_task,
            models_temporal.CompleteTaskRequest(taskId=id),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

```

#### Task Five: Processing Response(create_task_process__response)

The original code is an Asynchronous task waiting for its completion. The new code changes to Synchronous and adds the ability to claim and complete the task; we add a routine that generates a random number to emulate the response of any external system in charge of processing the invoice. Here is where you can call a method of your activities that connects to a CRM, database engine, or anything else you need.

```python
  async def create_task_process__response(self, processId: str):
        """Create task "Process Response" in KuFlow and wait for its completion"""

        id = workflow.uuid4()

        task_definition = models.TaskDefinitionSummary(code=self.TASK_CODE_PROCESS_RESPONSE)
        task = models.Task(id=id, process_id=processId, task_definition=task_definition)

        # HERE: Generates a random number to serve as a response from the system processing emulation
        number = str(random.randrange(1000, 2000, 3))
        
        # HERE: Initializes the element values of the task
        # Assigns the random number as the value of the task element named "RESPONSE"
        task.element_values = {}
        task.element_values["RESPONSE"] = [models.TaskElementValueString(value=number)]

        # HERE: Modifiy the activity to create the task using KuFlowSyncActivities.create_task
        await workflow.execute_activity(
            KuFlowSyncActivities.create_task,
            models_temporal.CreateTaskRequest(task=task),
            start_to_close_timeout=self._kuflow_activity_async_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_async_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        # HERE: Add this section to execute the activity to claim the task using KuFlowSyncActivities.claim_task
        await workflow.execute_activity(
            KuFlowSyncActivities.claim_task,
            models_temporal.ClaimTaskRequest(taskId=id),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        # HERE: Add this section to executes the activity to complete the task using KuFlowSyncActivities.complete_task
        await workflow.execute_activity(
            KuFlowSyncActivities.complete_task,
            models_temporal.CompleteTaskRequest(taskId=id),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )
```

Now we have to modify the "workflow run" method. The main change is the execution of some tasks, which after the modification will be dependent on the completion of others. As you will see, we assign the result of the first task to a variable (task_id), pass it as an argument to the second task, and repeat the same in the third.

Having something like this:

```python
@workflow.run
    async def run(
        self, request: models_temporal.WorkflowRequest
    ) -> models_temporal.WorkflowResponse:
        workflow.logger.info(f"Process {request.processId} started")

        task_id = await self.create_task_invoice__upload(request.processId)
        final_data = await self.create_task_file__processing(request.processId, task_id)
        await self.create_task_data__validation(request.processId, final_data)
        await self.create_task_invoice__processing(request.processId)
        await self.create_task_process__response(request.processId)
        await self.complete_process(request.processId)

        return models_temporal.WorkflowResponse(
            f"Completed process {request.processId}"
        )
```

The final step with the code is including the imports needed for this tutorial using some feature of your IDE (*like pressing **SHIFT+ ALT + O** in Visual Studio Code*).

## Testing

We can test all that we have done by running the “worker.py” (*like pressing **F5** in Visual Studio Code*) using the interpreter correspondig of your virtual environment, in our case  `Python 3.11.2('.venv':poetry)`:

<div class="text--center">

![](/img/TUT14-07-Test_1.png)

</div>

And initiating the process in KuFlow’s UI.

<div class="text--center">

![](/img/TUT14-07-Test_2.png)

</div>

Select a file to upload and complete the task, we use the [invoice example](https://github.com/Hec-KuFlow/KuFlow-ExtractInvoiceData/blob/main/invoice_1.jpg).

<div class="text--center">

![](/img/TUT14-07-Test_3.png)

</div>

After the progress activity finalization, validate the data, and then answer whether or not you want to process the invoice data.

<div class="text--center">

![](/img/TUT14-07-Test_4.png)

</div>

You will receive an invoice processing confirmation number.

<div class="text--center">

![](/img/TUT14-07-Test_5.png)

</div>

## Summary

In this tutorial, we have covered the basics of creating a Temporal.io-based workflow in KuFlow with Python and its OCR libraries. We have defined a new process definition, and we have built a workflow that contemplates the following business rules involving automated and human tasks:

1. Users in the organization can upload a new file with an invoice format.
2. The file uploaded will be analyzed, and information will be extracted from it according to what is requested by the business process.
3. An activity will show the data in KuFlow's UI and let the user modify it (if necessary) and decide whether to process the invoice by an external system or not.
4. The result of the processing will be shown on the screen.

We have created a special video with the entire process:

Here you can watch all steps in this video:

<a href="https://youtu.be/nTLGa2zheF0" target="_blank" title="Play me!">
  <p align="center">
	<img width="75%" src="https://img.youtube.com/vi/nTLGa2zheF0/maxresdefault.jpg" alt="Play me!"/>
  </p>
</a>

We sincerely hope that this step-by-step guide will help you to understand better how KuFlow can help your business to have better and more solid business processes.
