import { useMutation } from "@tanstack/react-query";
import axios from "axios";

const sendUserMessage = async (messagePayload) => {
    const response = await axios.post("https://9du0w7tqe7.execute-api.us-east-1.amazonaws.com/generate/answer", {
        ...messagePayload
    });
    
    return response.data;
}

export default function useSendUserMessage() {
    return useMutation({
        mutationFn: async (messagePayload) => await sendUserMessage(messagePayload),
        onSuccess: () => console.log("question sent successfully"),
        onError: (error) => console.log("error in asking bot question", error)
    })
}