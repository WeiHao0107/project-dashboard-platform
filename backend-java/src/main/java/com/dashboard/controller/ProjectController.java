package com.dashboard.controller;

import com.dashboard.dto.DepartmentDto;
import com.dashboard.dto.ProjectDto;
import com.dashboard.entity.Project;
import com.dashboard.repository.DepartmentRepository;
import com.dashboard.repository.ProjectRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/projects")
@RequiredArgsConstructor
public class ProjectController {

    private final ProjectRepository projectRepo;
    private final DepartmentRepository departmentRepo;

    @GetMapping
    public List<ProjectDto> listProjects() {
        return projectRepo.findAllByOrderByNameAsc().stream()
                .map(p -> new ProjectDto(p.getId(), p.getKey(), p.getName(), p.getDescription()))
                .toList();
    }

    @GetMapping("/{projectKey}/departments")
    public ResponseEntity<List<DepartmentDto>> listDepartments(@PathVariable String projectKey) {
        Project project = projectRepo.findByKey(projectKey)
                .orElseThrow(() -> new RuntimeException("Project not found: " + projectKey));

        List<DepartmentDto> depts = departmentRepo
                .findByProjectIdOrderByNameAsc(project.getId())
                .stream()
                .map(d -> new DepartmentDto(d.getId(), d.getName()))
                .toList();

        return ResponseEntity.ok(depts);
    }
}
