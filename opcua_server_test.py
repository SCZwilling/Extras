
from opcua import ua, Server


if __name__ == "__main__":

    server=Server()
    url="opc.tcp://127.0.0.2:500"
    server.set_endpoint(url)

    name="OPCUA_Simulation_Server"
    idx=server.register_namespace(name)

    # get Objects node, this is where we should put our custom stuff
    objects = server.get_objects_node()

    # populating our address space
    myobj = objects.add_object(idx, "MyObject")
    node1= myobj.add_object(idx,"node1")

    # Creating a custom event: Approach 1
    # The custom event object automatically will have members from its parent (BaseEventType)

    etype = server.create_custom_event_type(idx, 'MyFirstEvent', ua.ObjectIds.OffNormalAlarmType, [('MyNumericProperty', ua.VariantType.Float), ('MyStringProperty', ua.VariantType.String)])
    myevgen = server.get_event_generator(etype,myobj)

    # Creating a custom event: Approach 2
    custom_etype = server.nodes.base_event_type.add_object_type(2, 'MySecondEvent')
    custom_etype.add_property(2, 'MyIntProperty', ua.Variant(0, ua.VariantType.Int32))
    custom_etype.add_property(2, 'MyBoolProperty', ua.Variant(True, ua.VariantType.Boolean))

    mysecondevgen = server.get_event_generator(custom_etype, node1)

    # starting!
    server.start()

    try:
        # time.sleep is here just because we want to see events in UaExpert
        import time
        count = 0
        while True:
            time.sleep(5)
            myevgen.event.Message = ua.LocalizedText("Vijayant %d" % count)
            myevgen.event.Severity = count
            myevgen.event.MyNumericProperty = count
            myevgen.event.MyStringProperty = "Vijayant " + str(count)
            myevgen.trigger()
            
            mysecondevgen.event.MyIntProperty=count%3
            mysecondevgen.trigger(message="Vijayant %d" % count)
            count += 1
    finally:
        # close connection, remove subcsriptions, etc
        server.stop()