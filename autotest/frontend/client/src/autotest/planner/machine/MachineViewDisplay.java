package autotest.planner.machine;

import autotest.common.ui.NotifyManager;
import autotest.planner.TestPlannerDisplay;
import autotest.planner.TestPlannerTableDisplay;
import autotest.planner.TestPlannerTableImpl;

import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Panel;
import com.google.gwt.user.client.ui.SimplePanel;


public class MachineViewDisplay implements TestPlannerDisplay, MachineViewPresenter.Display {

    private Panel container = new SimplePanel();

    @Override
    public void initialize(HTMLPanel htmlPanel) {
        htmlPanel.add(container, "machine_view_main");
    }

    @Override
    public void clearAllData() {
        container.clear();
    }

    @Override
    public void setLoading(boolean loading) {
        NotifyManager.getInstance().setLoading(loading);
        container.setVisible(!loading);
    }

    @Override
    public TestPlannerTableDisplay generateMachineViewTableDisplay() {
        TestPlannerTableImpl display = new TestPlannerTableImpl();
        container.add(display);
        return display;
    }
}
