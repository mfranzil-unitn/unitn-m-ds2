package it.unitn.ds2.gui;

import it.unitn.ds2.gui.components.ApplicationContext;
import it.unitn.ds2.gui.view.MainView;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.event.EventHandler;
import javafx.scene.Scene;
import javafx.stage.Stage;
import javafx.stage.WindowEvent;


public class App extends Application {
    private final static double WINDOW_WIDTH = 1200;
    private final static double WINDOW_HEIGHT = 800;

    private ApplicationContext applicationContext;

    @Override
    public void start(Stage primaryStage) {
        applicationContext = new ApplicationContext();

        var mainView = new MainView(applicationContext);
        var scene = new Scene(mainView, WINDOW_WIDTH, WINDOW_HEIGHT);

        primaryStage.setOnCloseRequest(event -> {
            Platform.exit();
            System.exit(0);
        });
        primaryStage.setTitle("Raft cluster simulator");
        primaryStage.setScene(scene);

        primaryStage.show();
    }

    @Override
    public void stop() {
        applicationContext.terminate();
    }
}
