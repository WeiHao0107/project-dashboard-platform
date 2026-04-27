package com.dashboard.controller;

import com.dashboard.handler.MemberSummaryHandler;
import jakarta.persistence.EntityManager;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

import java.util.Optional;

@RestController
@RequestMapping("/api/projects/{projectKey}")
@RequiredArgsConstructor
public class MemberPerformanceController {

    private final MemberSummaryHandler handler;
    private final EntityManager em;

    @GetMapping("/member-performance")
    public List<Map<String, Object>> get(
            @PathVariable String projectKey,
            @RequestParam Optional<Integer> year,
            @RequestParam Optional<Long> departmentId) {

        return handler.query(projectKey, year.orElse(null), departmentId.orElse(null), em);
    }
}
