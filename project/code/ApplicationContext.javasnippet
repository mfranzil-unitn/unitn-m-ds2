package it.unitn.ds2.gui.components;

import akka.actor.typed.ActorSystem;

public class ApplicationContext {
    public final CommandBus commandBus;
    public final EventBus eventBus;

    public ApplicationContext() {
        var actorSystem = ActorSystem.create(SimulationController.create(this), "raft-cluster");
        commandBus = new CommandBus(actorSystem);
        eventBus = new EventBus();

    }

    /**
     * Terminates all the components of the application.
     */
    public void terminate() {
        commandBus.terminate();
        eventBus.terminate();
    }
}
