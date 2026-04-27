package com.dashboard.handler;

import com.dashboard.dto.IssueTrendResponse;
import com.dashboard.dto.IssueTrendResponse.SeriesData;
import com.dashboard.dto.IssueTrendResponse.SeriesPoint;
import jakarta.persistence.EntityManager;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.*;

@Component
public class IssueTrendHandler {

    private static final String[] MONTHS = {
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    };

    public IssueTrendResponse query(String projectKey, Integer year, Long departmentId,
                                    EntityManager em) {
        if (year == null) year = LocalDateTime.now().getYear();
        long deptParam = departmentId != null ? departmentId : -1L;

        String createdSql = """
            SELECT CAST(EXTRACT(MONTH FROM i.created_at) AS INTEGER) AS month, COUNT(*) AS cnt
            FROM issues i
            LEFT JOIN members m ON i.assignee_id = m.id
            LEFT JOIN departments d ON m.department_id = d.id
            WHERE i.project_id = (SELECT id FROM projects WHERE key = :key)
              AND EXTRACT(YEAR FROM i.created_at) = :year
              AND (:deptId = -1 OR d.id = :deptId)
            GROUP BY month
            ORDER BY month
            """;

        String resolvedSql = """
            SELECT CAST(EXTRACT(MONTH FROM i.resolved_at) AS INTEGER) AS month, COUNT(*) AS cnt
            FROM issues i
            LEFT JOIN members m ON i.assignee_id = m.id
            LEFT JOIN departments d ON m.department_id = d.id
            WHERE i.project_id = (SELECT id FROM projects WHERE key = :key)
              AND i.resolved_at IS NOT NULL
              AND EXTRACT(YEAR FROM i.resolved_at) = :year
              AND (:deptId = -1 OR d.id = :deptId)
            GROUP BY month
            ORDER BY month
            """;

        Map<Integer, Integer> createdMap  = runMonthQuery(em, createdSql,  projectKey, year, deptParam);
        Map<Integer, Integer> resolvedMap = runMonthQuery(em, resolvedSql, projectKey, year, deptParam);

        List<SeriesPoint> cData = new ArrayList<>();
        List<SeriesPoint> rData = new ArrayList<>();
        int cCum = 0, rCum = 0;
        for (int m = 1; m <= 12; m++) {
            cCum += createdMap.getOrDefault(m, 0);
            rCum += resolvedMap.getOrDefault(m, 0);
            cData.add(SeriesPoint.builder().x(MONTHS[m - 1]).y(cCum).build());
            rData.add(SeriesPoint.builder().x(MONTHS[m - 1]).y(rCum).build());
        }

        return IssueTrendResponse.builder()
                .series(List.of(
                    SeriesData.builder().name("Created").data(cData).build(),
                    SeriesData.builder().name("Resolved").data(rData).build()
                ))
                .build();
    }

    @SuppressWarnings("unchecked")
    private Map<Integer, Integer> runMonthQuery(EntityManager em, String sql,
                                                String projectKey, int year, long deptId) {
        var query = em.createNativeQuery(sql)
                      .setParameter("key", projectKey)
                      .setParameter("year", year)
                      .setParameter("deptId", deptId);

        Map<Integer, Integer> result = new HashMap<>();
        for (Object[] row : (List<Object[]>) query.getResultList()) {
            result.put(((Number) row[0]).intValue(), ((Number) row[1]).intValue());
        }
        return result;
    }
}
