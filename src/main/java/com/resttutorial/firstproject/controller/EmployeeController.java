package com.resttutorial.firstproject.controller;
import com.resttutorial.firstproject.converter.EmployeeConverter;
import com.resttutorial.firstproject.model.Employee;
import com.resttutorial.firstproject.repository.EmployeeRepository;
import com.resttutorial.firstproject.resource.EmployeeResource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.stream.Collectors;

@RestController
public class EmployeeController {

    private final EmployeeRepository employeeRepository;

    @Autowired
    public EmployeeController(EmployeeRepository employeeRepository) {
        this.employeeRepository = employeeRepository;
    }


    @GetMapping("/employees")
    public ResponseEntity<?> all() {

        List<EmployeeResource> employeeResources = employeeRepository
                .findAll()
                .stream()
                .map(employee -> EmployeeConverter.toResource(employee))
                .collect(Collectors.toList());

        return new ResponseEntity<>(employeeResources, HttpStatus.OK);
    }

    @PostMapping("/employees")
    public ResponseEntity<?> newEmployee(@RequestBody EmployeeResource employeeResource) {
        employeeRepository.save(EmployeeConverter.toEntity(employeeResource));
        return new ResponseEntity<>(employeeResource, HttpStatus.CREATED);
    }

    @GetMapping("/employees/{id}")
    public ResponseEntity<EmployeeResource> one(@PathVariable Long id) {

        Employee employee = employeeRepository.getOne(id);
        EmployeeResource employeeResource = EmployeeConverter.toResource(employee);
        return new ResponseEntity<>(employeeResource, HttpStatus.OK);
    }

    @PutMapping("/employees/{id}")
    public ResponseEntity<?> replaceEmployee(@RequestBody EmployeeResource employeeResource, @PathVariable Long id) {

        Employee employee = employeeRepository.findById(id)
                .map(emp -> {
                    emp.setRole(employeeResource.getRole());
                    emp.setLastName(employeeResource.getLastname());
                    emp.setFirstName(employeeResource.getFirstName());
                    return employeeRepository.save(emp);
                }).orElseGet(() -> {
                    return employeeRepository.save(EmployeeConverter.toEntity(employeeResource));
                });

        return new ResponseEntity<>(employeeResource, HttpStatus.OK);
    }

    @DeleteMapping("/employees/{id}")
    public ResponseEntity<?> deleteEmployee(@PathVariable Long id){

        employeeRepository.deleteById(id);
        return ResponseEntity.noContent().build();
    }


}
