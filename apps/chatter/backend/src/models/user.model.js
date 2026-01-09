import mongoose from "mongoose";

const userSchema = new mongoose.Schema({
    email: {
        type: String,
        required: true,
        unique: true,
    },
    fullName: {
        type: String,
        required: true,
    },
    password: {
        type: String,
        unique: true,
        minlength: 6
    },
    profilePic: {
        type: String,
        default: ""
    }
},
    { timestamps: true }// createdAt & updatedAt
);
//to show when the user created and updated their account

const User = mongoose.model("User", userSchema);

export default User;