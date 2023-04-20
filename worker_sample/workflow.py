from datetime import timedelta
import random
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from kuflow_rest import models
    from kuflow_temporal_activity_kuflow import models as models_temporal
    from kuflow_temporal_activity_kuflow import KuFlowSyncActivities
    from kuflow_temporal_activity_kuflow import KuFlowAsyncActivities
    from worker_sample.activities import InvoiceActivities, InvoiceDataExtractionRequest, InvoiceDataExtractionResponse


@workflow.defn(name="IDEWorker")
class SampleWorkflow:
    TASK_CODE_PROCESS_RESPONSE = "RESPONSE_TASK"
    TASK_CODE_DATA_VALIDATION = "IMGRESP"
    TASK_CODE_INVOICE_PROCESSING = "INVOICE_PROCESS_TASK"
    TASK_CODE_INVOICE_UPLOAD = "FILEUPLOADTASK"
    TASK_CODE_FILE_PROCESSING = "FILE_PROCESS_TASK"

    _default_retry_policy = RetryPolicy()
    _kuflow_activity_sync_start_to_close_timeout = timedelta(minutes=10)
    _kuflow_activity_sync_schedule_to_close_timeout = timedelta(days=365)
    _kuflow_activity_async_start_to_close_timeout = timedelta(days=1)
    _kuflow_activity_async_schedule_to_close_timeout = timedelta(days=365)

    async def create_task_process__response(self, processId: str):
        """Create task "Process Response" in KuFlow and wait for its completion"""

        id = workflow.uuid4()

        task_definition = models.TaskDefinitionSummary(code=self.TASK_CODE_PROCESS_RESPONSE)
        task = models.Task(id=id, process_id=processId, task_definition=task_definition)
        number = str(random.randrange(1000, 2000, 3))
        task.element_values = {}
        task.element_values["RESPONSE"] = [models.TaskElementValueString(value=number)]

        await workflow.execute_activity(
            KuFlowSyncActivities.create_task,
            models_temporal.CreateTaskRequest(task=task),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        await workflow.execute_activity(
            KuFlowSyncActivities.claim_task,
            models_temporal.ClaimTaskRequest(taskId=id),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )
        
        await workflow.execute_activity(
            KuFlowSyncActivities.complete_task,
            models_temporal.CompleteTaskRequest(taskId=id),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

    async def create_task_data__validation(self, processId: str, final_data: InvoiceDataExtractionResponse):
        """Create task "Data Validation" in KuFlow and wait for its completion"""

        id = workflow.uuid4()

        task_definition = models.TaskDefinitionSummary(
            code=self.TASK_CODE_DATA_VALIDATION
        )
        task = models.Task(
            id=id, process_id=processId, task_definition=task_definition
        )

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

    async def create_task_invoice__processing(self, processId: str):
        """Create task "Invoice Processing" in KuFlow and wait for its completion"""

        id = workflow.uuid4()

        task_definition = models.TaskDefinitionSummary(
            code=self.TASK_CODE_INVOICE_PROCESSING
        )
        task = models.Task(
            id=id, process_id=processId, task_definition=task_definition
        )

        await workflow.execute_activity(
            KuFlowSyncActivities.create_task,
            models_temporal.CreateTaskRequest(task=task),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )
        await workflow.execute_activity(
            KuFlowSyncActivities.claim_task,
            models_temporal.ClaimTaskRequest(taskId=id),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )
        await workflow.execute_activity(
            KuFlowSyncActivities.append_task_log,
            models_temporal.AppendTaskLogRequest(
                taskId=id,
                log=models.Log(
                    message="Procesando Archivo", level=models.LogLevel.INFO
                ),
            ),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        await workflow.execute_activity(
            KuFlowSyncActivities.append_task_log,
            models_temporal.AppendTaskLogRequest(
                taskId=id,
                log=models.Log(message="Archivo Procesado", level=models.LogLevel.INFO),
            ),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        await workflow.execute_activity(
            KuFlowSyncActivities.complete_task,
            models_temporal.CompleteTaskRequest(taskId=id),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

    async def create_task_invoice__upload(self, processId: str) -> str:
        """Create task "Invoice Upload" in KuFlow and wait for its completion"""

        id = workflow.uuid4()

        task_definition = models.TaskDefinitionSummary(
            code=self.TASK_CODE_INVOICE_UPLOAD
        )
        task = models.Task(
            id=id, process_id=processId, task_definition=task_definition
        )

        await workflow.execute_activity(
            KuFlowAsyncActivities.create_task_and_wait_finished,
            models_temporal.CreateTaskRequest(task=task),
            start_to_close_timeout=self._kuflow_activity_async_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_async_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        return id

    # agrego task_id: str
    async def create_task_file__processing(self, processId: str, upload_task_id: str) -> InvoiceDataExtractionResponse:
        """Create task "File Processing" in KuFlow and wait for its completion"""

        id = workflow.uuid4()

        task_definition = models.TaskDefinitionSummary(
            code=self.TASK_CODE_FILE_PROCESSING
        )
        task = models.Task(
            id=id, process_id=processId, task_definition=task_definition
        )

        await workflow.execute_activity(
            KuFlowSyncActivities.create_task,
            models_temporal.CreateTaskRequest(task=task),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )
        await workflow.execute_activity(
            KuFlowSyncActivities.claim_task,
            models_temporal.ClaimTaskRequest(taskId=id),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )
        await workflow.execute_activity(
            KuFlowSyncActivities.append_task_log,
            models_temporal.AppendTaskLogRequest(
                taskId=id,
                log=models.Log(
                    message="Procesando Archivo", level=models.LogLevel.INFO
                ),
            ),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        final_data = await workflow.execute_activity(
            InvoiceActivities.invoice_data_extraction,
            InvoiceDataExtractionRequest(task_id=upload_task_id),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        await workflow.execute_activity(
            KuFlowSyncActivities.append_task_log,
            models_temporal.AppendTaskLogRequest(
                taskId=id,
                log=models.Log(message="Archivo Procesado", level=models.LogLevel.INFO),
            ),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

        await workflow.execute_activity(
            KuFlowSyncActivities.complete_task,
            models_temporal.CompleteTaskRequest(taskId=id),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )
        
        return final_data

    async def complete_process(self, processId: str):
        """Complete Workflow"""

        await workflow.execute_activity(
            KuFlowSyncActivities.complete_process,
            models_temporal.CompleteProcessRequest(processId),
            start_to_close_timeout=self._kuflow_activity_sync_start_to_close_timeout,
            schedule_to_close_timeout=self._kuflow_activity_sync_schedule_to_close_timeout,
            retry_policy=self._default_retry_policy,
        )

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
