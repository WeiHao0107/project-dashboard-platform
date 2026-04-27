package com.dashboard.handler;

import com.dashboard.dto.WidgetDataResponse;
import com.dashboard.dto.WidgetQueryRequest;
import jakarta.persistence.EntityManager;

public interface WidgetDataHandler {
    String getSourceKey();
    WidgetDataResponse query(WidgetQueryRequest request, EntityManager em);
}
