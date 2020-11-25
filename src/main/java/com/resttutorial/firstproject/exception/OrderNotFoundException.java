package com.resttutorial.firstproject.exception;

public class OrderNotFoundException extends RuntimeException{

    public OrderNotFoundException(Long id){
        super("Order not found exception : " + id);
    }
}
