#!/usr/bin/env python3
"""
    This Project is a Python based HP ALM Purge Wizard.
    This is the main file which do all stuff
    For detailed informatin please visit
    https://github.com/aytuncbeken/Hp-Alm-Purge-Tool

    Author:Aytunc BEKEN
    Python Version:3.6
    License:GPL
"""
import threading
from concurrent.futures import ThreadPoolExecutor
import AlmConnector
import json
import time
import logging
import configparser
from datetime import datetime


# Global variable for Thread Access
delete_success = 0
delete_fail = 0
delete_total = 0
delete_wait_counter = 0
lock = threading.Lock()


def main():
    global delete_total
    global delete_success
    global delete_fail
    global delete_wait_counter
    global lock
    threadPool = ThreadPoolExecutor(max_workers=10)
    start_time = time.time()
    config = configparser.ConfigParser()
    config.read("PurgeWizard.ini")
    alm_host = config["PurgeWizard"]["AlmHost"]
    alm_port = config["PurgeWizard"]["AlmPort"]
    alm_username = config["PurgeWizard"]["AlmUserName"]
    alm_password = config["PurgeWizard"]["AlmPassword"]
    alm_domain = config["PurgeWizard"]["AlmDomain"]
    alm_project = config["PurgeWizard"]["AlmProject"]
    limit_per_page = config["PurgeWizard"]["RecordLimitPerPage"]
    date_limit = config["PurgeWizard"]["DeleteOlderThan"]
    simulate_delete = config["PurgeWizard"]["SimulateDelete"]
    log_file = config["PurgeWizard"]["LogFileWithFullPath"]
    delete_with_thread = config["PurgeWizard"]["DeleteWithThread"]
    logging.basicConfig(format='[%(asctime)s][%(levelname)s:] %(message)s', filename=log_file, filemode='w',
                        level=logging.INFO)
    logging.info("Starting Alm Purge Wizard with Parameters")
    logging.info("AlmHost:%s",alm_host)
    logging.info("AlmPort:%s", alm_port)
    logging.info("AlmUserName:%s", alm_username)
    logging.info("AlmPassword:%s", alm_password)
    logging.info("AlmDomain:%s", alm_domain)
    logging.info("AlmProject:%s", alm_project)
    logging.info("RecordLimitPerPage:%s", limit_per_page)
    logging.info("DeleteOlderThan:%s", date_limit)
    logging.info("SimulateDelete:%s", simulate_delete)
    logging.info("LogFileWithFullPath:%s", log_file)
    if not AlmConnector.connect_alm(alm_host, alm_port, alm_username, alm_password,alm_domain,alm_project):
        logging.info("Alm Connection failed")
        return
    if not AlmConnector.check_authentication():
        logging.info("Alm Auth Check Failed")
        return
    if not AlmConnector.get_session():
        logging.info("Alm Session Init Failed")
        return
    logging.info("Alm Connection/Authentication Succeeded")
    temp_response = AlmConnector.get_testset_list_with_only_id(None, None)
    if temp_response is None:
        logging.info("Test Set List Returned None - Exit")
        return
    test_list = json.loads(temp_response)
    test_count = test_list["TotalResults"]
    limit = limit_per_page
    offset = 0
    offset_step = int(limit)
    limit_date = datetime.strptime(date_limit,"%Y-%m-%d")
    logging.info("Total Test Set Entity Count: %s", test_count)
    logging.info("Iterate Over Test Sets - Limit:%s", limit)
    logging.info("Date Limit:%s", limit_date)
    while True:
        logging.info("Iterate Offset:%s" , offset)
        temp_response = AlmConnector.get_testset_list_with_only_id(limit, offset)
        if temp_response is None:
            logging.info("Test Set List Returned None - Exit")
            logging.info("Temp Response:%s", temp_response)
            return
        testset_list = json.loads(temp_response)
        testset_count = testset_list["TotalResults"]
        if testset_count == 0:
            logging.info("Test Set List Returned Zero Records - End Of Loop")
            logging.info("Test Set List:%s", testset_list)
            break
        logging.info("Number Of Records to Process:%s", len(testset_list["entities"]))
        for testset in testset_list["entities"]:
            testset_id = testset["Fields"][0]["values"][0]["value"]
            testset_name = testset["Fields"][1]["values"][0]["value"]
            logging.info("")
            logging.info("Processing Test Set Id:%s Test Set Name:%s", testset_id, testset_name)
            if testset_id is None:
                logging.info("Test Set Id is None - Pass Test")
                logging.info("Test Set:%s", testset)
                logging.info("Test Set Id:%s", testset_id)
                continue
            temp_response = AlmConnector.get_testcycl_list_by_test_set(testset_id)
            if temp_response is None:
                logging.info("Test Set Cycle List From Test Set Id Query Returned None - Exit")
                logging.info("Temp Response:%s" , temp_response)
                break
            cycle_json = json.loads(temp_response)
            cycle_list = {}
            for cycle in cycle_json["entities"]:
                cycle_id = cycle["Fields"][2]["values"][0]["value"]
                cycle_name = cycle["Fields"][1]["values"][0]["value"]
                cycle_list[cycle_id] = cycle_name
            logging.info("Test Set Cycle List Extracted From Test Set:%s", testset_id)
            logging.info("Test Cycle List:%s",cycle_list)
            logging.info("Number Of Test Cycles:%s", len(cycle_list))
            for cycle in cycle_list:
                logging.info("Test Cycle:%s - %s", cycle, cycle_list[cycle])
                temp_response = AlmConnector.get_run_by_testcycl(cycle)
                run_list = json.loads(temp_response)
                run_total_results = run_list["TotalResults"]
                logging.info("Number Of Run:%s",run_total_results)
                if run_total_results == 1:
                    logging.info("Test Cycle Have 1 Run - Keeping - Pass Test")
                    continue
                if run_total_results == 0:
                    logging.info("Test Cycle Have No Run - Pass Test")
                    continue
                for run in run_list["entities"]:
                    run_id = run["Fields"][0]["values"][0]["value"]
                    execution = run["Fields"][1]["values"][0]["value"]
                    execution_date = datetime.strptime(execution, "%Y-%m-%d")
                    date_diff = execution_date - limit_date
                    logging.info("Processing Run Id:%s Execution Date:%s Date Diff:%s" ,run_id, execution_date, date_diff )
                    if int(date_diff.days) >= 0:
                        logging.info("Execution Date is not under limit - Pass Test")
                        continue
                    if run_id is None:
                        logging.info("Run Id is None - Pass Run")
                        logging.info("Run:%s",run)
                        logging.info("Run Id:%s",run_id)
                        continue
                    if run_list["entities"].index(run) >= len(run_list["entities"]) -1:
                        logging.info("Leaving Most Recent Test - Pass Test")
                        continue
                    delete_total = delete_total + 1
                    if simulate_delete == "False":
                        if delete_with_thread == "True":
                            logging.info("Delete Run:%s With Thread",run_id)
                            lock.acquire()
                            delete_wait_counter = delete_wait_counter + 1
                            lock.release()
                            threadPool.submit(delete_run,run_id)
                        else:
                            logging.info("Delete Run:%s Without Thread", run_id)
                            delete_run(run_id)
                    else:
                        logging.info("(SimulateDelete) Pass Delete Run::%s ", run_id)
        offset = offset + offset_step
    elapsed_time = time.time() - start_time
    threadPool.shutdown(wait=True)
    logging.info("Purge Ended")
    logging.info("Elapsed Time:%s",elapsed_time)
    logging.info("Total Run Marked For Delete:%s", delete_total)
    logging.info("Total Run Delete Success:%s", delete_success)
    logging.info("Total Run Delete Failed:%s",delete_fail)


def delete_run(run_id):
    global delete_success
    global delete_fail
    global delete_wait_counter
    global lock
    logging.info("Ready Delete Run Id:%s ", run_id)
    if AlmConnector.delete_run(run_id):
        logging.info("Run Deleted - Run Id:%s", run_id)
        delete_success = delete_success + 1
    else:
        logging.info("##ERROR##Run Deleted Failed - Run Id:%s", run_id)
        delete_fail = delete_fail + 1
    lock.acquire()
    delete_wait_counter = delete_wait_counter - 1
    logging.info("Delete Wait Run Number:%s",delete_wait_counter)
    logging.info("Total Run Delete Success:%s", delete_success)
    lock.release()

main()
