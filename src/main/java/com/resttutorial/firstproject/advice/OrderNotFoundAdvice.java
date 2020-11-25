package com.resttutorial.firstproject.advice;

import com.resttutorial.firstproject.exception.OrderNotFoundException;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.ResponseStatus;

@ControllerAdvice
public class OrderNotFoundAdvice {

    @ResponseBody
    @ExceptionHandler(OrderNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    String OrderNotFoundHandler(OrderNotFoundException ex){
        return ex.getMessage();
    }
}
