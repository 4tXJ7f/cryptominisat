#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto
import sys
import boto.ec2
from boto.ec2.connection import EC2Connection
import ConfigParser, os, socket
import pprint


class SpotRequestor:
    def __init__(self):
        self.conf = ConfigParser.ConfigParser()
        self.conf.read('ec2-spot-instance.cfg')
        self.ec2conn = self.__create_ec2conn()
        if self.ec2conn is None:
            print 'Unable to create EC2 ec2conn'
            sys.exit(0)

    def __create_ec2conn(self):
        ec2conn = EC2Connection()
        regions = ec2conn.get_all_regions()
        for r in regions:
            if r.name == self.conf.get('ec2', 'region'):
                ec2conn = EC2Connection(region = r)
                return ec2conn
        return None

    def __provision_instance(self, user_data):
        self.reqs = self.ec2conn.request_spot_instances(price = self.conf.get('ec2', 'max_bid'),
                count = int(self.conf.get('ec2', 'count')),
                image_id = self.conf.get('ec2', 'ami_id'),
                subnet_id = self.conf.get('ec2', 'subnet_id'),
                instance_type = self.conf.get('ec2', 'type'),
                instance_profile_arn = self.conf.get('ec2', 'instance_profile_arn'),
                user_data = user_data,
                key_name = self.conf.get('ec2', 'key_name'),
                security_group_ids = [self.conf.get('ec2', 'security_group')])

        print "Request created, got back: "
        pprint.pprint(self.reqs)

    def __get_spot_price(self):
        price_history = self.ec2conn.get_spot_price_history(instance_type = self.conf.get('ec2', 'type'),
                                                            product_description = 'Linux/UNIX')

        pprint.pprint(self.conf.get('ec2', 'type'))
        pprint.pprint(price_history)

    def create_spots(self):
        user_data = "valami"

        spot_price = self.__get_spot_price()
        print 'Spot price is ' + str(spot_price)
        self.__provision_instance(user_data)

        for req in self.reqs:
            print 'req state: %s req ID (if launched): %s' %(req.state, req.instance_id)

class OLD:
    def __init__(self):
        self.conn = boto.ec2.connect_to_region(self.conf.get("ec2", "region"))

    def get_reservations(self):
        reservations = self.conn.get_all_reservations()
        num = 0
        instances = []
        for reservation in reservations:
            for instance in reservation.instances:
                if instance.instance_type != "t2.micro":
                    instances.append([instance.instance_type, instance.placement])

        print "ec2conn instances running:", instances

    def get_spot_requests(self):
        requests = self.conn.get_all_spot_instance_requests()
        print "Active requests:", requests
        for req in requests:
            if ("%s" % req.status) != "<Status: instance-terminated-by-user>":
                print "-> ", [req.price, req.status]
