local Public = {}

function Public.foo()
	return "foo"
end

function Public.bar()
	return "bar"
end

function Public.foo_bar()
	return Public.foo() .. Public.bar()
end

return Public
