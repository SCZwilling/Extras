package main

import (
	"fmt"
	"syscall"
	"unsafe"
)

type POINT struct {
	X float64
	Y float64
}

func windowFromPoint(x, y float64) (syscall.Handle, uintptr, error) {
	user32 := syscall.NewLazyDLL("user32.dll")
	windowFromPoint := user32.NewProc("WindowFromPoint")
	pt := POINT{X: x, Y: y}
	ret, a, err := windowFromPoint.Call(uintptr(unsafe.Pointer(&pt)))
	return syscall.Handle(ret), a, err
}

func main() {
	hwnd, a, b := windowFromPoint(float64(200), float64(200))
	fmt.Println(hwnd, a, b)
}
