local Public = {}

function Public.foo()
	return "foo"
end

function Public.bar()
	return "bar"
end

function Public.foobar()
	return Public.foo() .. Public.bar()
end

return Public
