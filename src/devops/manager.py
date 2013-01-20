import ipaddr
from devops.helpers.helpers import generate_mac
from devops.helpers.network import IpNetworksPool
from devops.models import Address, Interface, Node, Network, Environment

class Manager(object):
    def create_environment(self, name):
        return Environment.objects.create(name=name)

    def list_environments(self):
        return Environment.objects.all()

    def get_environment(self, name):
        return Environment.objects.get(name=name)

    def erase_environment(self, environment):
        environment.erase()

    def snapshot_environment(self, environment, name):
        environment.snapshot(name)

    def revert_environment(self, environment, name):
        environment.revert(name)

    def suspend_environment(self, environment):
        environment.suspend()

    def resume_environment(self, environment):
        environment.resume()

    def create_network_pool(self, networks, prefix):
        return IpNetworksPool(networks=networks, prefix=prefix)

    def _get_default_pool(self):
        return self.create_network_pool(networks=[ipaddr.IPNetwork('10.0.0.0/16')], prefix=24)

    def create_network(
        self, name, environment, ip_network=None, pool=None, has_dhcp_server=True, has_pxe_server=False,
        forward='route'):
        allocated_network = ip_network or environment.allocate_network(pool or self._get_default_pool())
        return Network.objects.create(environment=environment, name=name, ip_network=ip_network or allocated_network,
            has_pxe_server=has_pxe_server, has_dhcp_server=has_dhcp_server, forward=forward)

    def create_node(self, name, environment, role=None, vcpu=2,
                    memory=1024, has_vnc=True, metadata=None, hypervisor='kvm',
                    os_type='hvm', architecture='x86_64', boot=None):
        if not boot: boot = ['network', 'cdrom', 'hd']
        node = Node.objects.create(name=name, environment=environment, role=role, vcpu=vcpu, memory=memory,
            has_vnc=has_vnc, metadata=metadata, hypervisor=hypervisor, os_type=os_type, architecture=architecture,
            )
        node.boot = boot
        return node

    #class DiskDeviceManager(models.Manager):
    #    pass

    #class VolumeManager(models.Manager):
    #    def __init__(self, capacity=None, path=None, format='qcow2', base_image=None):
    #    pass

    def upload(self, path):
        pass

    def _generate_mac(self):
        return generate_mac()

    def create_interface(self, network, node, type='network', target_dev=None, mac_address=None, model='virtio'):
        interface = Interface.objects.create(network=network, node=node, type=type, target_dev=target_dev,
            mac_address=mac_address or self._generate_mac(), model=model)
        interface.add_address(str(network.next_ip()))
        return interface

    def create_address(self, ip_address, interface):
        Address.objects.create(ip_address=ip_address, interface=interface)
