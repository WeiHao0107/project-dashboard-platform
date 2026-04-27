package com.dashboard.controller;

import com.dashboard.dto.IssueTrendResponse;
import com.dashboard.handler.IssueTrendHandler;
import jakarta.persistence.EntityManager;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;

@RestController
@RequestMapping("/api/projects/{projectKey}")
@RequiredArgsConstructor
public class IssueTrendController {

    private final IssueTrendHandler handler;
    private final EntityManager em;

    @GetMapping("/issue-trend")
    public IssueTrendResponse get(
            @PathVariable String projectKey,
            @RequestParam Optional<Integer> year,
            @RequestParam Optional<Long> departmentId) {

        return handler.query(projectKey, year.orElse(null), departmentId.orElse(null), em);
    }
}
