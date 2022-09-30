;   example of compiled for loop output
(bytecode
    ; loop from 0 to 10 in steps of size 1, add register 1 to register 0
    (loadk 0 0)     ;   set register 0 to 0
    (loadk 1 1)     ;   set register 1 to 1

    (loadk 2 0)     ;   i
    (loadk 3 10)    ;   end
    (loadk 4 1)     ;   step size

    (eq 2 3)        ;   i == end
    (cjmp 2)        ;   if true, jump to end
    (add 0 1)       ;   add register 1 to register 0
    (add 2 4)       ;   i += step size
    (jmp -4)        ;   go to top of loop

    (halt)
)

;   example of same loop in asm form
;   asm form lets you set branch targets, and lets you use labels, and variables and macros
(asm
    ; loop from 0 to 10 in steps of size 1, add register 1 to register 0
    (loadk 0 0)     ;   set register 0 to 0
    (loadk 1 1)     ;   set register 1 to 1

)


; example use of "for macro" to generate looped code
(for (i 0 10 1)
    (add 0 1)
)

;   example of partly compiled for macro
(asm
    (let ((i 0) (end 10) (step 1))
        (loadk 0 ,i)
        (loadk 1 ,step)
    )

(defmacro for (i start end step) body
    '(asm
        (loadk 0 ,start)
        (loadk 1 ,step)
        (loadk 2 ,start)
        (loadk 3 ,end)
        (eq 2 3)
        (cjmp 2)
        ,(compile body)
        (add 2 1)
        (jmp ,(add -4 (length (compile body))))
    )
)


; example of integer vector type
(defmacro make-vec (t)
    '(defstruct vec (type ,t) (size 3) (data (make-array size)))
)

; example use
(make-vec int)

; example of vector addition function
(defn vec-add (a b)
    (let ((c (make-vec)))
        (for (i 0 (vec-size a) 1)
            (set (vec-ref c i) (+ (vec-ref a i) (vec-ref b i)))
        )
        c
    )
)
