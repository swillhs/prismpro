# -*- coding: utf-8 -*-

# pylint: disable=invalid-name, wrong-import-order, ungrouped-imports
# pylint: disable=wrong-import-position, no-member, unused-argument
# pylint: disable=no-self-use

"""
Copyright (c) 2020 Nutanix Inc. All rights reserved.
Author: sundara.sundar@nutanix.com
"""
from framework.exceptions.entity_error import NuTestEntityOperationError
from framework.entities.group.rest_group import RESTGroup
from framework.lib.nulog import INFO

from workflows.manageability.api.aplos.aplos_client import AplosClient
from workflows.manageability.api.aplos import tasks_api
from workflows.prism_ops.common.aiops_api_helper import AiopsApiHelper
import workflows.prism_ops.common.consts as xdisc_config


class XDiscApiUtil(object):
  """
  XDiscover API utility to handle all xdiscovery related API request/response.
  """
  PAGE_LIMIT = 100
  DISC_RULE_API_EP = "xdiscovery/rules"
  DISC_APPS_API_EP = "xdiscovery/apps"
  CLOUD_CONFIG_API = "xdiscovery/cloudConfig"
  VCENTER_CONFIG = "xdiscovery/vcenterConfigs"
  CLUSTER_CONFIG = "xdiscovery/discoveryConfig"
  APPS_SUMMARY = "xdiscovery/summary"
  V1_BASE_URL = "https://{pc_ip}:9440/PrismGateway/services/rest/v1/aiops/" \
                "v2.r0.a1/"
  GROUPS_URL = "https://{pc_ip}:9440/api/nutanix/v3/groups"

  def __init__(self, pc, **kwargs):
    """
    Initialize Actions Service Util
    Args:
      pc(cluster): PC Cluster
      kwargs(dict): Args for later use
    """
    self.pc_cluster = pc

    self.pc_ip = self.pc_cluster.svm_ips[0]
    self.api_helper = AiopsApiHelper(pc_ip=self.pc_ip)
    self.pc_aplos_client = AplosClient(self.pc_ip)
    self.group = RESTGroup(self.pc_cluster)

  def get_verified_apps(self, query_filter):
    """
    Get discovered app list for given filter criteria.

    Args:
      query_filter(str): Query Filter for the payload

    Returns:
      list: List of discovered apps
    """
    INFO("Get verified apps...")
    payload = {
      "filter": query_filter,
      "page": {"start_": 0, "limit_": XDiscApiUtil.PAGE_LIMIT}
    }
    resp = self.api_helper.handle_post_request(
      rel_url="{}/list".format(XDiscApiUtil.DISC_APPS_API_EP),
      payload=payload)

    return resp.get("data").get("discovered_apps") if resp else []

  def run_discovery(self):
    """
    Start discovery app process.

    Returns:
      bool: True if succeed
    """
    INFO("Run Discovery...")
    rel_url = "{}/$actions/discover" . format(XDiscApiUtil.DISC_APPS_API_EP)
    response = self.api_helper.handle_post_request(rel_url=rel_url, payload={})

    if isinstance(response, bool):
      return False
    else:
      task_id = response.get("data").get("ext_id")
      return self.check_task_complete([task_id])

  def verify_apps(self, app_ids=None):
    """
    Verify discovered apps.

    Args:
      app_ids(list): List of App UUIDs
    Returns:
      None
    """
    INFO("Run verify apps for apps ids: {}" . format(app_ids))
    rel_url = "{}/$actions/verify" . format(XDiscApiUtil.DISC_APPS_API_EP)
    payload = {}
    if app_ids is not None:
      payload = {
        "ext_ids": app_ids
      }
    response = self.api_helper.handle_post_request(rel_url=rel_url,
                                                   payload=payload)
    task_id = response.get("ext_id")
    return self.check_task_complete([task_id])

  def export_apps(self, discovery_version=None, latest_discovery=True):
    """
    Export discovered apps.

    Args:
      discovery_version(str): Discovery version uuid to commit
      latest_discovery(bool): True to get latest discovery version
    Returns:
      None
    """
    if latest_discovery:
      discovery_version = self.get_entities_from_group(
        entity_name="discovery_version", attribute_list=["uuid"],
        query_filter="latest_discovery==true").keys()[0]

    INFO("Committing App discovery version: '{}'" .format(discovery_version))
    rel_url = "{}/{}/$actions/commit" . format(XDiscApiUtil.DISC_APPS_API_EP,
                                               discovery_version)

    self.api_helper.handle_post_request(rel_url=rel_url, payload={})

  def create_discovery_rule(self, app_name, tcp_ports=None, udp_ports=None,
                            vm_list=None, description=None):
    """
    Create discovery mapping rule with the given information.

    Args:
      app_name(str): App Name
      tcp_ports(list): List of TCP ports
      udp_ports(list): List of UDP ports
      vm_list(list): VM uuid list
      description(str): Rule description

    Returns:
      None
    """
    INFO("Create discovery rule for app name: '{}'" . format(app_name))
    rule_name = "{}_disc_rule" . format(app_name)
    payload = {
      "app_name": app_name,
      "rule_name": rule_name,
      "rule_description": description or "Description of {}" . format(rule_name)
    }

    if tcp_ports:
      payload["tcp_ports"] = tcp_ports
    if udp_ports:
      payload["udp_ports"] = udp_ports
    if vm_list:
      scope = []
      for vm in vm_list:
        scope.append({"ext_id": vm})
      payload["scope"] = scope

    self.api_helper.handle_post_request(rel_url=XDiscApiUtil.DISC_RULE_API_EP,
                                        payload=payload)

  def get_discovery_rule(self, rule_id):
    """
    Get discovery mapping rule for the given rule id.

    Args:
      rule_id(str): Rule uuid

    Returns:
      dict: Discovery Rule map
    """
    INFO("Get discovery rule for id: {}" . format(rule_id))
    response = self.api_helper.handle_get_request(
      rel_url="{}/{}" . format(XDiscApiUtil.DISC_RULE_API_EP, rule_id))
    return response

  def get_all_discovery_rules(self, system_rule=False):
    """
    Get all discovery mapping rule defined in the system.

    Args:
      system_rule(bool): If True include 'System Rules'

    Returns:
      dict: Discovery Rule map
    """
    INFO("Get all discovery rules")
    response = self.api_helper.handle_get_request(
      rel_url="{}" . format(XDiscApiUtil.DISC_RULE_API_EP))

    if system_rule:
      return response.get("data")

    return [rule for rule in response.get("data")
            if rule.get("discovery_type") != 1]

  def update_discovery_rule(self, app_name, update_name=None,
                            tcp_ports=None, udp_ports=None,
                            description=None, vm_list=None):
    """
    Update a discovery Rule with given ports.
    Args:
      app_name(str): Existing App Name
      update_name(str): App Name to be updated
      tcp_ports(list): TCP Ports
      udp_ports(list): UDP Ports
      description(str): Rule description
      vm_list(list): VM list to update

    Returns:
      bool: True if succeeded
    """
    INFO("Update discovery rule for app name: {}" . format(app_name))
    all_disc_rules = self.get_all_discovery_rules()

    disc_rule = next((rule for rule in all_disc_rules
                      if rule.get("app_name").lower() ==
                      app_name.lower()), None)

    INFO("Discovery Rule: {}" . format(disc_rule))
    if not disc_rule:
      INFO("App rule for app '{}' does not exist")
      return

    scope = []
    if vm_list:
      for vm in vm_list:
        scope.append({"ext_id": vm})
      disc_rule["scope"] = scope

    existing_scope = disc_rule.get("scope", None)

    disc_rule["rule_name"] = disc_rule["rule_name"]
    disc_rule["app_name"] = update_name or disc_rule["app_name"]
    disc_rule["tcp_ports"] = tcp_ports or disc_rule["tcp_ports"]
    disc_rule["udp_ports"] = udp_ports or disc_rule["udp_ports"]
    disc_rule["rule_description"] = description or "{} updated" . format(
      disc_rule["rule_description"])

    del disc_rule["discovery_type"]

    if scope is None and existing_scope:
      disc_rule["scope"] = existing_scope

    self.api_helper.handle_put_request(
      rel_url="{}/{}" . format(XDiscApiUtil.DISC_RULE_API_EP,
                               disc_rule.get('ext_id')), payload=disc_rule)

  def delete_discovery_rule(self, app_name):
    """
    Delete discovery mapping rule thats associated to given app name.

    Args:
      app_name(str): app name

    Returns:
      None
    """
    INFO("Delete discovery rule for app name: {}".format(app_name))
    all_disc_rules = self.get_all_discovery_rules()

    disc_rule = next((rule for rule in all_disc_rules if
                      rule.get("app_name", "").lower() == app_name.lower()),
                     None)

    INFO("Disc Rule: {}" . format(disc_rule))
    if disc_rule and len(disc_rule) == 0:
      INFO("App rule for app '{}' does not exist")
      return

    self.api_helper.handle_delete_request(
      rel_url="{}/{}" . format(XDiscApiUtil.DISC_RULE_API_EP,
                               disc_rule[0].get("ext_id")))

  def delete_discovery_rules(self, rule_ids):
    """
    Delete discovery rules that matches given app names list
    Args:
      rule_ids(list): Rule Id List

    Returns:
      None
    """
    INFO("Delete discovery rules for ids: {}" . format(rule_ids))

    payload = {
      "ext_ids": rule_ids
    }
    self.api_helper.handle_post_request(
      rel_url="{}/$actions/delete" . format(XDiscApiUtil.DISC_RULE_API_EP),
      payload=payload)

  def enable_discovery_rules(self, rule_ids, enable=False):
    """
    Enable discovery rules that matches given app names list
    Args:
      rule_ids(list): Rule Id List
      enable(bool): True to enable, False to disable

    Returns:
      None
    """
    INFO("{} discovery rules for ids: {}".format("Enable" if enable
                                                 else "Disable", rule_ids))

    payload = {
      "enable": enable,
      "ext_ids": rule_ids
    }
    self.api_helper.handle_post_request(
      rel_url="{}/$actions/enable".format(XDiscApiUtil.DISC_RULE_API_EP),
      payload=payload)

  def add_clusters(self, payload):
    """
    Add clusters

    Args:
      payload(dict): Payload for add clusters

    Returns:
      bool: True if task is completed
    """

    response = self.api_helper.handle_post_request(
      rel_url="{}/$actions/config" . format(XDiscApiUtil.CLUSTER_CONFIG),
      payload=payload
    )
    task_id = response.get("ext_id")
    return self.check_task_complete([task_id])

  def create_cloud_config(self, cloud_config=None):
    """
    Create Cloud config using the given parameters and poll for task to
    complete.

    Args:
      cloud_config(dict): Cloud config
                          {
                            "api_key": "12333-323232".
                            "key_id": "abc-321-3321"
                          }
    Returns:
      bool: True if task succeed
    """
    cloud_config = cloud_config or xdisc_config.TEST_CLOUD_CONFIG1
    api_key = cloud_config.get("api_key")
    key_id = cloud_config.get("key_id")

    payload = {
      "api_key": api_key,
      "key_id": key_id
    }

    response = self.api_helper.handle_post_request(
      rel_url="{}/$actions/config" . format(XDiscApiUtil.CLOUD_CONFIG_API),
      payload=payload
    )

    task_id = response.get("ext_id")
    return self.check_task_complete([task_id])

  def create_vcenter_config(self, vcenterip=None, username=None, password=None):
    """
    Create vCenter config to enable 'netflow' in vDS and check for task id
    status complete.

    Args:
      vcenterip(str): vCenter IP
      username(str): vCenter User Name
      password(str): vCenter Password

    Returns:
      bool: True if Task succeeds
    """
    vcenterip = vcenterip or xdisc_config.VCENTER_IP
    username = username or xdisc_config.VCENTER_USER
    password = password or xdisc_config.VCENTER_PASSWORD

    payload = {
      "username": username,
      "password": password,
      "hostname": vcenterip
    }

    response = self.api_helper.handle_post_request(
      rel_url=XDiscApiUtil.VCENTER_CONFIG,
      payload=payload
    )
    vcenter_id = response.get("ext_id")
    return vcenter_id

  def update_vcenter_config(self, vcenter_map=None):
    """
    Update vCenter config in vDS and check for task id status complete.

    Args:
      vcenter_map(dict): vCenter IP as key and User Name, Password dict as value
                          {"xx.xx.xx.x": {"username": "abc", "password":"321"}}

    Returns:
      bool: True if Task succeeds
    """
    vcenterConfigs = self.get_vcenter_config()
    vcenter_map_system = dict((cluster.get('ip_address'), uuid)
                              for uuid, cluster in vcenterConfigs.iteritems())
    INFO("Existing vCenter Config: {}".format(vcenter_map_system))

    if vcenter_map is None:
      vcenter_map = {}
      for cluster in vcenterConfigs.values():
        vcenter_map[cluster.get('ip_address')] = {
          "username": xdisc_config.VCENTER_USER,
          "password": xdisc_config.VCENTER_PASSWORD
        }

    task_ids = []
    for ip, cred in vcenter_map.iteritems():
      payload = {
        "username": cred.get("username"),
        "password": cred.get("password"),
        "hostname": ip
      }
      uuid = vcenter_map_system.get(ip)
      response = self.api_helper.handle_put_request(
        rel_url="{}/{}" . format(XDiscApiUtil.VCENTER_CONFIG, uuid),
        payload=payload
      )
      task_ids.append(response.get("ext_id"))

    return self.check_task_complete(task_ids)

  def start_service(self, service="XdiscoveryService"):
    """
    Enable xdiscovery service on PC

    Args:
      service(str): Service Name to be Enabled ('XdiscoveryService' or
        'DpmService')
    Returns:
      None
    """
    INFO("Start {} in PC" . format(service))
    base_url = XDiscApiUtil.V1_BASE_URL.format(pc_ip=self.pc_ip)
    url = "{}perfmon/{}/$actions/enable" . format(base_url, service)
    response = self.api_helper.handle_request(url=url, method="post",
                                              payload={})
    return response.get("data").get("code")

  def check_service_enabled(self, service="XdiscoveryService"):
    """
    Check xdiscovery service enabled/running on PC

    Args:
      service(str): Service Name to be Enabled ('XdiscoveryService' or
        'DpmService')
    Returns:
      None
    """
    INFO("Check {} running in PC" . format(service))
    base_url = XDiscApiUtil.V1_BASE_URL.format(pc_ip=self.pc_ip)
    url = "{}perfmon/status/{}" . format(base_url, service)
    response = self.api_helper.handle_request(url=url, method="get")
    if response.get("data").get("code").lower() == "true":
      INFO("{} running..." . format(service))
      return True
    INFO("{} NOT running..." . format(service))
    return False

  def enable_xdisc_on_clusters(self, esx_cluster_map=None,
                               ahv_cluster_list=None):
    """
    Enable xdiscovery on given list of AHV and ESX clusters, check for task
    status complete.

    Args:
      esx_cluster_map(map): cluster uuid UUID vcenter uuid map
      ahv_cluster_list(list): UUID list of AHV cluster

    Returns:
      bool: True if task succeed
    """

    clusters = []
    if esx_cluster_map:
      for cluster_uuid, vcenter_uuid in esx_cluster_map.iteritems():
        clusters.append({
          "hypervisor_type": "kVMware",
          "vcenter_id": vcenter_uuid,
          "cluster_uuid": cluster_uuid
        })

    if ahv_cluster_list:
      for uuid in ahv_cluster_list:
        clusters.append({
          "hypervisor_type": "AHV",
          "cluster_uuid": uuid
        })

    payload = {
      "clusters": clusters
    }

    response = self.api_helper.handle_post_request(
      rel_url="{}/$actions/config" . format(XDiscApiUtil.CLUSTER_CONFIG),
      payload=payload
    )

    task_id = response.get("ext_id")
    return self.check_task_complete([task_id])

  def get_discovered_apps(self, query_filter=None):
    """
    Get all data provider in the system.

    Args:
      query_filter(str): Filter to get the apps

    Returns:
      dict: Data provider map
            {'Nutanix Netflow': {"uuid": "1234-432w-dsds", "enabled":"true"},
             'Nutanix vCenter': {"uuid": "1324-412w-dsds", "enabled":"false"}}
    """
    self.run_discovery()

    if query_filter is None:
      query_filter = "latest_discovery==true;(tcp_port_list!=[no_val]," \
               "udp_port_list!=[no_val])"

    INFO("Get discovered Apps with filter: {}" .format(query_filter))
    payload = {
      "entity_type": "discovery_result",
      "group_member_attributes": [
        {"attribute": "app_name"},
        {"attribute": "app_state"},
        {"attribute": "verified"},
        {"attribute": "vm_name"},
        {"attribute": "tcp_port_list"},
        {"attribute": "udp_port_list"},
        {"attribute": "mapping_rule"},
        {"attribute": "discovery_timestamp"}],
      "filter_criteria": query_filter
    }
    try:
      apps = self.group.list(cluster=self.pc_cluster, data_json=payload,
                             json=True)
    except NuTestEntityOperationError:
      INFO("No group data found yet")
      return {}
    apps_data_map = self._get_data_map(apps)
    return apps_data_map

  def get_xdisc_enabled_clusters(self):
    """
    Get list of clusters that has xdiscovery feature enabled.

    Returns:
      list: List of clusters
    """
    response = self.api_helper.handle_get_request(
      rel_url=XDiscApiUtil.CLUSTER_CONFIG)
    return response.get("clusters")

  def get_entities_from_group(self, entity_name, attribute_list,
                              query_filter=None):
    """
    Get Entity info from groups call.

    Args:
      entity_name(str): Entity Name
      attribute_list(str): List of attributes
      query_filter(str): Filter to get the apps

    Returns:
      dict: Data provider map
            {'entity_uuid1': {"name": "name1", "enabled":"true"},
             'entity_uuid2': {"name": "name2", "enabled":"false"}}
    """
    INFO("Get {} from groups api call" .format(entity_name))

    if query_filter is None:
      query_filter = ""

    attributes = []
    for att in attribute_list:
      attributes.append({"attribute": att})

    payload = {
      "entity_type": entity_name,
      "group_member_attributes": attributes,
      "filter_criteria": query_filter
    }
    INFO("Payload: {}" . format(payload))
    try:
      entities = self.group.list(cluster=self.pc_cluster, data_json=payload,
                                 json=True)
    except NuTestEntityOperationError:
      INFO("No results from groups API")
      return {}

    entity_map = self._get_data_map(entities)
    return entity_map

  def get_vcenter_config(self):
    """
    Get vcenter configuration

    Returns:
      dict: vcenter config
    """
    attrib_list = ["name", "ip_address", "data_provider_name"]
    return self.get_entities_from_group(entity_name="external_entity_config",
                                        attribute_list=attrib_list)

  def get_cloud_config(self):
    """
    Get cloud configuration.

    Returns:
      dict: cloud config
    """
    attrib_list = ["type", "key"]
    return self.get_entities_from_group(
      entity_name="external_entity_shareable_config",
      attribute_list=attrib_list)

  def get_cluster_config(self):
    """
    Get Cluster configuration.

    Returns:
      dict: cluster config
    """
    attrib_list = ["cluster_uuid", "cluster_name", "config_json"]
    return self.get_entities_from_group(
      entity_name="external_entity_config_xdiscovery",
      attribute_list=attrib_list)

  def check_task_complete(self, task_id_list, timeout=120):
    """
    Check for given task id complete.
    Args:
      task_id_list(list): List of task Ids
      timeout(int): Timeout value

    Returns:
      bool: True if succeeds
    """
    INFO("Task Id List: {}" . format(task_id_list))
    return tasks_api.poll_task(self.pc_aplos_client,
                               task_uuid_list=task_id_list,
                               timeout=timeout, poll_interval=2)

  def get_apps_summary(self):
    """
    Get apps summary
    Returns:
      dict: App summary map
    """
    summary_list = ["discovered_apps", "committed_apps", "clusters",
                    "cloud_connection", "enabled_discovery_rules",
                    "vcenters_status_summary", "collectors_status_summary"]
    payload = {"fields": summary_list}
    response = self.api_helper.handle_post_request(
      rel_url=XDiscApiUtil.APPS_SUMMARY, payload=payload)
    summary_details = response.get("data").get("summary")

    ret_summary = {}
    for summary in summary_list:
      ret_summary.update({summary: summary_details.get(summary).get("data")})

    INFO("Apps Summary: {}" . format(ret_summary))
    return ret_summary

  @staticmethod
  def _get_data_map(response):
    """
    Get Data map from given group response.
    Args:
      response(dict): Group response

    Returns:
      dict: Data in map format
    """
    ret_map = {}
    for entity in response:
      det_map = {}
      for data in entity.get("data"):
        values = data.get("values")
        if values:
          if len(values[0].get("values")) == 1 \
              and "_list" not in data.get("name"):
            det_map[data.get("name")] = values[0].get("values")[0]
          else:
            det_map[data.get("name")] = values[0].get("values")

        else:
          det_map[data.get("name")] = values
      ret_map[entity.get("entity_id")] = det_map
    return ret_map

if __name__ == "__main__":
  from framework.lib.nulog import set_level
  from framework.entities.cluster.prism_central_cluster import \
    PrismCentralCluster

  set_level(level=10)
  #pc_ip = "10.46.152.60"
  pc_ip = "10.53.121.134"
  #pc_ip = "10.45.32.151"
  test_pc = PrismCentralCluster(cluster=pc_ip)

  xdisc_api_util = XDiscApiUtil(pc=test_pc)
  res = xdisc_api_util.update_vcenter_config()
  INFO("RES: {}" . format(res))

