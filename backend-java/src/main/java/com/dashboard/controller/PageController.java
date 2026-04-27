package com.dashboard.controller;

import com.dashboard.dto.PageDto;
import com.dashboard.entity.Project;
import com.dashboard.repository.CustomPageRepository;
import com.dashboard.repository.ProjectRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/projects")
@RequiredArgsConstructor
public class PageController {

    private final ProjectRepository projectRepo;
    private final CustomPageRepository pageRepo;

    @GetMapping("/{projectKey}/pages")
    public ResponseEntity<List<PageDto>> listPages(@PathVariable String projectKey) {
        Project project = projectRepo.findByKey(projectKey)
                .orElseThrow(() -> new RuntimeException("Project not found: " + projectKey));

        List<PageDto> pages = pageRepo
                .findByProjectIdAndIsActiveTrueOrderBySortOrderAsc(project.getId())
                .stream()
                .map(p -> new PageDto(p.getPageKey(), p.getPageName(), p.getIcon(), p.getSortOrder()))
                .toList();

        return ResponseEntity.ok(pages);
    }
}
