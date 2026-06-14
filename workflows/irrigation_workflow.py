from workflows.base_workflow import (
    BaseWorkflow
)


class IrrigationWorkflow(
    BaseWorkflow
):

    async def execute(
        self,
        context
    ):

        city = context.get_input(
            "city"
        )

        weather = (
            context
            .resource_manager
            .get_capability(
                "weather"
            )
        )

        weather_data = (
            await weather.execute(
                {
                    "city": city
                }
            )
        )

        if weather_data[
            "temperature"
        ] > 30:

            recommendation = (
                "Increase irrigation"
            )

        else:

            recommendation = (
                "Normal irrigation"
            )

        return {
            "city":
                city,

            "weather":
                weather_data,

            "recommendation":
                recommendation
        }