package com.resttutorial.firstproject.converter;

import com.resttutorial.firstproject.model.Employee;
import com.resttutorial.firstproject.resource.EmployeeResource;

public class EmployeeConverter {

    public static EmployeeResource toResource(Employee employee){
        EmployeeResource employeeResource = new EmployeeResource();

        employeeResource.setFirstName(employee.getFirstName());
        employeeResource.setLastname(employee.getLastName());
        employeeResource.setRole(employee.getRole());

        return employeeResource;
    }

    public static Employee toEntity(EmployeeResource resource){
        Employee employee = new Employee();

        employee.setFirstName(resource.getFirstName());
        employee.setLastName(resource.getLastname());
        employee.setRole(resource.getRole());

        return employee;

    }


}
