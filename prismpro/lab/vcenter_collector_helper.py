#
# Copyrights (c) Nutanix Inc. 2020
# Author: abhishek.agrawal1@nutanix.com
#
"""
 Test cases focussing on metric descriptors for
 STATS API.
"""
# pylint: disable=fixme
# pylint: disable=protected-access
# pylint: disable=invalid-name
# pylint: disable=bare-except
# pylint: disable=too-many-locals
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-nested-blocks
# pylint: disable=too-many-statements
# pylint: disable=broad-except
# pylint: disable=no-member
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-lines
import json
import time

from framework.components.insights_server import InsightsServer
from framework.interfaces import consts
from framework.interfaces.http.http import HTTP
from framework.lib.nulog import INFO, STEP
from framework.entities.task.ecli_task import ECLITask
from workflows.stats_gw.app_monitoring.lib.bluemedora_helper \
  import BlueMedoraHelper
from workflows.stats_gw.app_monitoring import const
from workflows.stats_gw.app_monitoring import vcenter_metrics_list

VC_ENTITY_TYPES = [
  "vm",
  "container",
  "cluster",
  "node"]

class VcenterCollectorHelper(object):
  """
   Test cases focussing on metric descriptors for STATS API.
  """
  def __init__(self, pc_cluster, provider, stats_port=9440):
    """
    __init__
    Args:
      pc_cluster(obj): PC object
      provider(any): provider name
      stats_port(any): Stats gateway port
    """
    self.pc_cluster = pc_cluster
    self.bmhelper = BlueMedoraHelper(pc_cluster, provider,
                                     "nutanix_vcenter", stats_port=9440)
    self.pc_ip = self.bmhelper.get_vip(self.pc_cluster)
    self.http_client = HTTP(retries=2)
    self.http_client._session.auth = (consts.PRISM_USER, consts.PRISM_PASSWORD)
    self.ecli_client = ECLITask(cluster=self.pc_cluster)
    self.dpm_url = "https://%s:9440/api/aiops/v4.r0.a1/perfmon" % self.pc_ip
    self.provider = provider
    self.stats_port = stats_port
    self.insights_server = InsightsServer(self.pc_cluster, start_rpc=True)

  @staticmethod
  def get_all_supported_metrics_for_uda(pc_ip):
    """
    get_all_supported_metrics_for_uda
    Args:
      pc_ip(str): pc_ip
    Returns:

    """
    url = "https://%s:9440/PrismGateway/services/rest" \
          "/v1/alerts/policies/supported_metrics" % pc_ip
    import requests
    headers = {'content-Type': 'application/json'}
    res = requests.get(url, headers=headers,
                       verify=False, timeout=30,
                       auth=(consts.PRISM_USER, consts.PRISM_PASSWORD))
    resp = res.json()
    entity_metrics = {}
    entities = resp["entities"]
    for entity in entities:
      if "vcenter" in entity["entityType"]:
        metrics = [metric["name"] for metric in entity["supportedMetrics"]]
        entity_metrics[entity["entityType"]] = metrics
    return entity_metrics

  @classmethod
  def get_entity_metrics_map(cls, endpoint_uuid):
    """
    Populate entity metrics and attribute map for collector
    Args:
      endpoint_uuid(str): UUID for endpoint
    Returns:
      entity_metrics_map(dict): Map of entity metrics and attributes
    """

    entity_metrics_map = {
      "vm": {
        "external_entity_config_uuid": endpoint_uuid,
        "metrics": vcenter_metrics_list.vm_metrics,
        "attributes": vcenter_metrics_list.vm_attributes
      },
      "container": {
        "external_entity_config_uuid": endpoint_uuid,
        "metrics": vcenter_metrics_list.container_metrics,
        "attributes": vcenter_metrics_list.container_attributes
      },
      "cluster": {
        "external_entity_config_uuid": endpoint_uuid,
        "metrics": vcenter_metrics_list.cluster_metrics,
        "attributes": vcenter_metrics_list.cluster_attributes
      },
      "node": {
        "external_entity_config_uuid": endpoint_uuid,
        "metrics": vcenter_metrics_list.node_metrics,
        "attributes": vcenter_metrics_list.node_attributes
      }
    }
    return entity_metrics_map

  def get_config_and_service(self):
    """
    Get the config for vcenter and the service name
    Returns:
      config(dict): config for vcenter
      service(str): service name
    """
    service = "dpm"
    config = const.vcenter_config
    config["ip_address"] = str(self.pc_ip)
    return config, service

  def setup_data_provider(self):
    """
    Setup the data provider for endpoint configuration
    """
    if not self.bmhelper.is_dpm_enabled():
      self.bmhelper.enable_dpm_service()
    if not self.bmhelper.is_provider_enabled(provider=self.provider):
      self.enable_collector()
    self.bmhelper.get_metric_data_provider(provider=self.provider)

  def cleanup_vcenter(self, svm):
    """
    cleanup_vcenter
    Args:
      svm(obj):
    Returns:
    """
    svm.execute("source /etc/profile; genesis stop dpm_server",
                ignore_errors=True)
    container_id = svm.execute(
      "docker ps -a -q --filter 'name=nutanix_vcenter'")["stdout"]
    while container_id:
      for container in container_id.split("\r\n"):
        svm.execute("docker stop %s && docker rm %s" % (
          container, container), ignore_errors=True)
      container_id = self.pc_cluster.execute(
        "docker ps -a -q --filter 'name=nutanix_vcenter'")["stdout"]

  def get_entities_for_entity_type(self, entity_type):
    """
    Get the entity list for an entity type
    Args:
      entity_type(str): entity type
    Returns:
      entity_list(list): list of dict of entity data
    """
    insights_csr = self.insights_server.get_entities(entity_type)

    entity_list = [] if 'entity' not in \
                        insights_csr.keys() else insights_csr['entity']
    return entity_list

  def get_target_schema(self, authentication=None):
    """
    Get schema uuid of the data provider
    Args:
      authentication(list): username and password list
    Returns:
      uuid(str): target schema uuid
    Raises: Schema not found Exception
    """
    url = self.dpm_url + "/target/schema?dataProviderName=%s" % self.provider
    if not authentication:
      authentication = (consts.PRISM_USER, consts.PRISM_PASSWORD)
    import requests
    res = requests.get(url=url, auth=authentication, verify=False)
    assert res.status_code == 200, "call to get schema failed"
    res = res.json()
    if not res:
      raise Exception("got empty response from get schema call")
    return res["data"][0]["uuid"]

  def disable_data_provider(self, authentication=None, status_code=None,
                            get_task_uuid=False):
    """
    disable_data_provider
    Args:
      authentication(str): username and password list
      status_code(str): status code to check
      get_task_uuid(bool): Flag to return task uuid
    Returns:
    """
    INFO("Disabling data provider")

    url = self.dpm_url + "/dataprovider/nutanix_vcenter/$actions/disable"
    if not authentication:
      authentication = (consts.PRISM_USER, consts.PRISM_PASSWORD)
    import requests
    res = requests.post(url=url,
                        auth=authentication,
                        verify=False)
    INFO("RESPONSE IS {}".format(res))
    if status_code:
      INFO("Test disable status_code: %s Expected: %s" % (
        res.status_code, status_code))
      INFO("status code is {}".format(status_code))
      INFO("RESPONSE IS {}".format(json.dumps(res.status_code)))
      assert str(status_code) in str(json.dumps(res.status_code)), \
        "status_code: %s Expected: %s" % (res.status_code, status_code)
    res = res.json()
    if get_task_uuid:
      return res["task_uuid"]
    response = self.bmhelper.poll_current_task(task_uuid=res["task_uuid"])
    INFO("RESPONSE TO TASK IS {}".format(response))

  def enable_collector(self, status_code=None, authentication=None):
    """
    enable collector
    Args:
      status_code(str): status code to check
      authentication(str): username and password list
    Returns:
    """
    url = self.dpm_url + "/dataprovider/nutanix_vcenter/$actions/enable"
    if not authentication:
      authentication = (consts.PRISM_USER, consts.PRISM_PASSWORD)
    import requests
    res = requests.post(url=url,
                        auth=authentication,
                        verify=False)
    INFO("RESPONSE IS {}".format(res.json()))
    if status_code:
      INFO("Test Connection status_code: %s Expected: %s" % (
        res.status_code, status_code))
      assert str(status_code) in str(json.dumps(res.status_code)), \
        "status_code: %s Expected: %s" % (res.status_code, status_code)
    res = res.json()
    INFO("RESPONSE IS {}".format(res))
    response = self.bmhelper.poll_current_task(task_uuid=res["task_uuid"])
    INFO("RESPONSE TO TASK IS {}".format(response))

  def create_target_instance(self, endpoint_json,
                             status_code="201",
                             duplicate_entity=False):
    """
    create_endpoint
    Args:
      endpoint_json(dict): endpoint config
      status_code(str): status code to check
      duplicate_entity(bool): boolean to check for duplicate entity
    Returns:
      endpoint_uuid(str): endpoint uuid of connection
    """
    url = self.dpm_url + "/target/instance?dataProviderName=%s" % self.provider
    STEP("Create Endpoint For the config: %s" % json.dumps(
      endpoint_json, indent=4))
    authentication = (consts.PRISM_USER, consts.PRISM_PASSWORD)
    import requests
    res = requests.post(url=url, json=endpoint_json,
                        auth=authentication,
                        verify=False)
    resp = res.json()
    assert str(status_code) in str(json.dumps(res.status_code)), \
      "status_code: %s Expected: %s" % (res.status_code, status_code)

    if "already exists" in str(resp.get("message")) and duplicate_entity:
      return True

    self.bmhelper.poll_current_task(task_uuid=resp["task_uuid"])
    entity_id = self.bmhelper.get_external_entity_config_uuids(
      name=endpoint_json["name"])[0]

    resp = self.bmhelper.get_target_instance(endpoint_uuid=entity_id)

    response = resp["app_config"]["config_json"]["connectionInfo"]
    for key in endpoint_json["app_config"]["config_json"]["connectionInfo"]:
      # we assign a random string for password and hence cannot be tested
      if key == "vCenter_Password":
        continue
      assert str(endpoint_json["app_config"]
                 ["config_json"]["connectionInfo"][key]).lower() == \
             str(response[key]).lower(), "assert failed for: %s" % key
    INFO("Response: %s" % json.dumps(resp, indent=4))
    endpoint_uuid = resp["app_config"]["uuid"]
    INFO("endpoint uuid is {}".format(endpoint_uuid))
    return endpoint_uuid

  def send_xstream_data(self, entity_type, entity_id,
                        metrics, value, cas_value, authentication=None,
                        status_code=None):
    """
    Send Xstream data
    Args:
      entity_type(str): Entity type
      entity_id(str): Entity id to update
      metrics(str): metrics to update
      value(Obj): value of metrics to update
      cas_value(int): new case value of entity
      authentication(list): username and password list
      status_code(int): status code to validate
    Returns:
      endpoint_uuid(str): endpoint uuid of connection
    """
    current_time = long(time.time()) * 10 ** 6
    INFO("current time is {}".format(current_time))
    data = [
      {
        "entity_type": "%s" % entity_type,
        "source": "%s" % self.provider,
        "entity_id": "%s" % entity_id,
        "metrics": [
          {
            "name": "%s" % metrics,
            "timeseries": {
              "values": [
                {
                  "int_val": value,
                  "timestamp_epoch": int(current_time),
                  "Debug": "VCenter Datasource [%s]=[%s]" % (metrics, value)
                }
              ]
            }
          }
        ],
        "cas_value": cas_value
      }
    ]
    INFO("DATA IS {}".format(data))
    url = "https://%s:9440/api/aiops/v4.r0.a1/stats/sources/%s/entities/%s" \
          % (self.pc_ip, self.provider, entity_type)
    import requests
    if not authentication:
      authentication = (consts.PRISM_USER, consts.PRISM_PASSWORD)
    res = requests.put(url=url, json=data,
                       auth=authentication,
                       verify=False)
    INFO("RESPONSE IS {}".format(str(json.dumps(res.status_code))))
    time.sleep(300)

    assert str(status_code) in str(json.dumps(res.status_code)), \
        "status_code: %s Expected: %s" % (res.status_code, status_code)

  def send_crud_operation(self, data, authentication=None):
    """
    Send an api to do crud operationon vm
    Args:
      data(dict): config for ap
      authentication(list): username and password list
    Returns:
    """

    url = "https://%s:9440/api/nutanix/v0.8/vms/set_power_state/fanout"\
          % self.pc_ip
    import requests
    if not authentication:
      authentication = (consts.PRISM_USER, consts.PRISM_PASSWORD)
    res = requests.post(url=url, json=data,
                        auth=authentication,
                        verify=False)
    INFO("DATA IS {}".format(data))
    INFO("RESPONSE IS {}".format(res.json()))
    res = res.json()
    response = self.bmhelper.poll_current_task(task_uuid=res["taskUuid"])
    INFO("status is {}".format(str(response["status"]).lower()))
    assert str("Failed").lower() in str(response["status"]).lower(), \
      "crud operation is possible on vcenter vm"
