package com.dashboard.handler;

import jakarta.persistence.EntityManager;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.*;

@Component
public class MemberSummaryHandler {

    private static final String[] MONTH_KEYS = {
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    };

    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> query(String projectKey, Integer year, Long departmentId,
                                           EntityManager em) {
        if (year == null) year = LocalDateTime.now().getYear();
        long deptParam = departmentId != null ? departmentId : -1L;

        String sql = """
            SELECT m.id, m.name,
                   CAST(EXTRACT(MONTH FROM i.resolved_at) AS INTEGER) AS month,
                   COUNT(*) AS cnt
            FROM issues i
            JOIN members m ON i.assignee_id = m.id
            JOIN departments d ON m.department_id = d.id
            WHERE i.project_id = (SELECT id FROM projects WHERE key = :key)
              AND i.resolved_at IS NOT NULL
              AND EXTRACT(YEAR FROM i.resolved_at) = :year
              AND (:deptId = -1 OR d.id = :deptId)
            GROUP BY m.id, m.name, CAST(EXTRACT(MONTH FROM i.resolved_at) AS INTEGER)
            ORDER BY m.name
            """;

        var q = em.createNativeQuery(sql)
                  .setParameter("key", projectKey)
                  .setParameter("year", year)
                  .setParameter("deptId", deptParam);

        Map<Long, String>               metaMap = new LinkedHashMap<>();
        Map<Long, Map<String, Integer>> pivot   = new LinkedHashMap<>();

        for (Object[] row : (List<Object[]>) q.getResultList()) {
            Long   mid   = ((Number) row[0]).longValue();
            String mname = (String) row[1];
            int    month = ((Number) row[2]).intValue();
            int    cnt   = ((Number) row[3]).intValue();

            metaMap.putIfAbsent(mid, mname);
            pivot.computeIfAbsent(mid, k -> new HashMap<>())
                 .put(MONTH_KEYS[month - 1], cnt);
        }

        // If no resolved issues, still show all members in the project/dept
        if (metaMap.isEmpty()) {
            String memberSql = departmentId == null
                ? "SELECT m.id, m.name FROM members m JOIN departments d ON m.department_id = d.id JOIN projects p ON d.project_id = p.id WHERE p.key = :key ORDER BY m.name"
                : "SELECT m.id, m.name FROM members m JOIN departments d ON m.department_id = d.id WHERE d.id = :deptId ORDER BY m.name";

            var mq = em.createNativeQuery(memberSql);
            if (departmentId == null) mq.setParameter("key", projectKey);
            else mq.setParameter("deptId", departmentId);

            for (Object[] row : (List<Object[]>) mq.getResultList()) {
                Long mid = ((Number) row[0]).longValue();
                metaMap.putIfAbsent(mid, (String) row[1]);
                pivot.putIfAbsent(mid, new HashMap<>());
            }
        }

        // Build rows
        List<Map<String, Object>> rows = new ArrayList<>();
        for (Long mid : metaMap.keySet()) {
            Map<String, Integer> monthly = pivot.getOrDefault(mid, Map.of());

            Map<String, Object> row = new LinkedHashMap<>();
            row.put("member", metaMap.get(mid));
            int total = 0;
            for (String mk : MONTH_KEYS) {
                int v = monthly.getOrDefault(mk, 0);
                row.put(mk, v);
                total += v;
            }
            row.put("total", total);
            rows.add(row);
        }

        return rows;
    }
}
