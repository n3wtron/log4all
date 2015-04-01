package jobs

type TestJob struct{}

func (j TestJob) Run() {
	println("ciao")
}
